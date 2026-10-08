"""
Tiny HTTP server (over a Unix socket, so it works with --network none) that runs
Python code in ONE persistent IPython shell. Variables survive between calls.

  POST /exec   {"code": "...", "timeout": 60}  -> stdout, stderr, error, result preview,
                                                  figures saved, new files, namespace diff, elapsed, rss_mb
  GET  /state                                  -> variables (type + shape), files in /workspace, rss_mb
  POST /reset                                  -> clear variables, close figures
  GET  /env                                    -> python + package versions, limits

Two watchdog threads end the process (run the container with --rm and Docker removes it):
  * idle:    no request for IDLE_MINUTES
  * storage: /workspace above WORKSPACE_GB -> newest files deleted until under the cap, then exit
Before exiting they write the reason to /workspace/_killed.txt so the host can tell the agent.
"""
import json, os, re, signal, socketserver, sys, threading, time
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.figure

_saved_by_code = set()                                   # ids of figures the cell saved itself (fig.savefig / plt.savefig)
_orig_savefig = matplotlib.figure.Figure.savefig
def _tracked_savefig(self, *a, **k):
    out = _orig_savefig(self, *a, **k)
    _saved_by_code.add(id(self))
    return out
matplotlib.figure.Figure.savefig = _tracked_savefig
import pandas as pd
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from traitlets.config import Config

WORKSPACE = Path("/workspace")
SOCKET = WORKSPACE / "exec.sock"
KILLED = WORKSPACE / "_killed.txt"
WORKSPACE_CAP = int(float(os.environ.get("WORKSPACE_GB", "1")) * 1e9)   # bytes allowed in /workspace
IDLE_SECONDS = float(os.environ.get("IDLE_MINUTES", "60")) * 60         # exit after this much inactivity
CLIP = 4000                                                             # max chars per text field
last_activity = time.time()

STARTUP = """
import numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns
DATA = "/data/aeronet.parquet"   # AERONET AOD L2 daily table (read-only)
"""

cfg = Config()
cfg.HistoryManager.enabled = False          # no sqlite history file (root fs is read-only)
cfg.InteractiveShell.colors = "nocolor"     # plain-text tracebacks
shell = InteractiveShell.instance(config=cfg)
shell.displayhook.write_output_prompt = lambda: None            # don't echo "Out[n]: ..." into stdout,
shell.displayhook.write_format_data = lambda *a, **k: None      # the last expression comes back as `result`
BASE_NAMES = set()
fig_counter = 0


# ── helpers ──────────────────────────────────────────────────────────────────
def clip(s):
    s = str(s)
    return s if len(s) <= CLIP else s[: CLIP // 2] + f"\n... [{len(s) - CLIP} chars clipped] ...\n" + s[-CLIP // 2:]


def describe(obj):
    """Type + shape, and for a DataFrame its first columns: 'DataFrame(6204, 5)[date, AOD_500nm, ...]'."""
    try:
        if isinstance(obj, pd.DataFrame):
            cols = [str(c) for c in obj.columns]
            shown = ", ".join(cols[:8]) + (f", ... {len(cols)} columns" if len(cols) > 8 else "")
            return f"DataFrame{obj.shape}[{shown}]"
        if isinstance(obj, (list, tuple, set, dict)):
            first = next(iter(obj.values() if isinstance(obj, dict) else obj), None)
            return f"{type(obj).__name__}({len(obj)}" + (f" of {type(first).__name__})" if first is not None else ")")
        shape = getattr(obj, "shape", None)
        return f"{type(obj).__name__}{tuple(shape)}" if shape is not None else type(obj).__name__
    except Exception:
        return type(obj).__name__


def preview(obj):
    if obj is None:
        return None
    if isinstance(obj, pd.DataFrame):
        return clip(f"DataFrame {obj.shape}\ndtypes:\n{obj.dtypes.to_string()}\n\n"
                    f"head:\n{obj.head().to_string()}\n\ntail:\n{obj.tail().to_string()}")   # to_string: never hide columns with ...
    return clip(repr(obj))


def user_vars():
    return {k: describe(v) for k, v in shell.user_ns.items() if k not in BASE_NAMES and not k.startswith("_")}


def snapshot():
    return {k: (id(v), describe(v)) for k, v in shell.user_ns.items()}


def files():
    return sorted(str(p.relative_to(WORKSPACE)) for p in WORKSPACE.rglob("*") if p.is_file() and p not in (SOCKET, KILLED))


def file_stamps():
    """{name: (mtime_ns, size)} of every file in /workspace: a cell that overwrites a file changes its stamp."""
    return {str(p.relative_to(WORKSPACE)): (p.stat().st_mtime_ns, p.stat().st_size)
            for p in WORKSPACE.rglob("*") if p.is_file() and p not in (SOCKET, KILLED)}


def workspace_bytes():
    return sum(p.stat().st_size for p in WORKSPACE.rglob("*") if p.is_file())


def memory_limit_mb():
    try:
        mem = Path("/sys/fs/cgroup/memory.max").read_text().strip()        # set by docker --memory
        return int(mem) // 1_000_000 if mem.isdigit() else None
    except OSError:
        return None
MEMORY_LIMIT_MB = memory_limit_mb()


def rss_mb():
    return int(open("/proc/self/statm").read().split()[1]) * os.sysconf("SC_PAGE_SIZE") // 1_000_000


def save_figures(new_files):
    """PNGs the cell wrote itself + auto-saved copies (fig_NNN.png) of figures it left unsaved; then close all."""
    global fig_counter
    saved = [f for f in new_files if f.lower().endswith(".png")]
    for n in plt.get_fignums():
        fig = plt.figure(n)
        if id(fig) in _saved_by_code:
            continue
        fig_counter += 1
        path = WORKSPACE / f"fig_{fig_counter:03d}.png"
        fig.savefig(path, dpi=100, bbox_inches="tight")
        saved.append(path.name)
    plt.close("all")
    _saved_by_code.clear()
    return saved


def _timeout(signum, frame):
    raise TimeoutError("cell exceeded its timeout")

signal.signal(signal.SIGALRM, _timeout)
signal.signal(signal.SIGTERM, lambda *a: sys.exit(0))   # so `docker stop` is instant


def die(reason):
    KILLED.write_text(reason)
    print(reason, flush=True)
    os._exit(3)


def idle_watchdog():
    while True:
        time.sleep(5)
        if time.time() - last_activity > IDLE_SECONDS:
            die(f"idle-stopped after {IDLE_SECONDS/60:g} min without a request")


def storage_watchdog():
    while True:
        time.sleep(1)
        used = workspace_bytes()
        if used > WORKSPACE_CAP:
            deleted = []
            for p in sorted((p for p in WORKSPACE.rglob("*") if p.is_file() and p != SOCKET),
                            key=lambda p: p.stat().st_mtime, reverse=True):     # newest first
                if used <= WORKSPACE_CAP:
                    break
                used -= p.stat().st_size
                p.unlink()
                deleted.append(p.name)
            die(f"storage cap exceeded: /workspace went over {WORKSPACE_CAP/1e9:g} GB. "
                f"Sandbox killed; newest files deleted to get back under the cap: {deleted}")


# ── the 4 operations ─────────────────────────────────────────────────────────
def reset():
    global BASE_NAMES
    shell.reset(new_session=False)
    plt.close("all")
    shell.run_cell(STARTUP, store_history=False)
    BASE_NAMES = set(shell.user_ns)


def column_hint(code, err):
    """For a column error (KeyError, AttributeError): the columns and dtypes of every DataFrame in the kernel that
    the cell names, appended to the error so the retry works from the real column list instead of a new guess."""
    if not isinstance(err, (KeyError, AttributeError)):
        return ""
    names = set(re.findall(r"[A-Za-z_]\w*", code))
    lines = []
    for name in sorted(names & set(shell.user_ns)):
        obj = shell.user_ns[name]
        if type(obj).__name__ == "DataFrame":
            cols = [f"{c} ({t})" for c, t in zip(obj.columns, obj.dtypes.astype(str))]
            lines.append(f"  {name} ({len(obj)} rows): " + ", ".join(cols[:80]) + (" ..." if len(cols) > 80 else ""))
    if not lines:
        return ""
    return "\ncolumns of the DataFrames this cell used (a name not listed does not exist in that frame):\n" + "\n".join(lines)


def exec_cell(code, timeout=60):
    before_ns, before_files, t0 = snapshot(), file_stamps(), time.time()
    signal.alarm(timeout)
    try:
        with capture_output(display=False) as cap:
            res = shell.run_cell(code, store_history=True)
    finally:
        signal.alarm(0)
    err = res.error_before_exec or res.error_in_exec
    after_ns = snapshot()
    after_files = file_stamps()
    new_files = sorted(f for f in after_files if after_files[f] != before_files.get(f))   # new OR overwritten
    figures = save_figures(new_files)
    new_files = [f for f in new_files if f not in figures]          # PNGs are reported once, under figures
    return {
        "ok": err is None,
        "timed_out": isinstance(err, TimeoutError),
        "error": repr(err) + column_hint(code, err) if err else None,
        "stdout": clip(cap.stdout),
        "stderr": clip(cap.stderr),
        "result": preview(res.result),
        "figures": figures,
        "new_files": new_files,
        "vars_new": {k: after_ns[k][1] for k in after_ns if k not in before_ns and not k.startswith("_")},
        "vars_changed": {k: after_ns[k][1] for k in after_ns if k in before_ns and after_ns[k] != before_ns[k] and not k.startswith("_")},
        "elapsed_s": round(time.time() - t0, 3),
        "rss_mb": rss_mb(),
        "memory_limit_mb": MEMORY_LIMIT_MB,
    }


def state():
    return {"vars": user_vars(), "files": files(), "workspace_mb": round(workspace_bytes() / 1e6, 2),
            "workspace_cap_mb": WORKSPACE_CAP // 1_000_000, "rss_mb": rss_mb(), "memory_limit_mb": MEMORY_LIMIT_MB}


def env():
    import numpy, pandas, matplotlib, seaborn, scipy, statsmodels, pyarrow, IPython, cartopy, shapely
    mem = Path("/sys/fs/cgroup/memory.max").read_text().strip()
    quota, period = Path("/sys/fs/cgroup/cpu.max").read_text().split()       # e.g. "200000 100000" = 2 CPUs
    return {"python": sys.version.split()[0],
            "packages": {"numpy": numpy.__version__, "pandas": pandas.__version__, "pyarrow": pyarrow.__version__,
                         "matplotlib": matplotlib.__version__, "seaborn": seaborn.__version__, "scipy": scipy.__version__,
                         "statsmodels": statsmodels.__version__, "cartopy": cartopy.__version__, "shapely": shapely.__version__,
                         "ipython": IPython.__version__},
            "memory_limit_mb": int(mem) // 1_000_000 if mem.isdigit() else mem,
            "cpus": int(quota) / int(period) if quota.isdigit() else os.cpu_count(), "workspace_cap_gb": WORKSPACE_CAP / 1e9, "data": "/data/aeronet.parquet",
            "preloaded": STARTUP.strip()}


# ── HTTP plumbing ────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def _send(self, obj, status=200):
        body = json.dumps(obj, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_one_request(self):
        global last_activity
        last_activity = time.time()          # a running cell is not idle
        super().handle_one_request()
        last_activity = time.time()

    def do_GET(self):
        routes = {"/state": state, "/env": env}
        self._send(routes[self.path]()) if self.path in routes else self._send({"error": "unknown endpoint"}, 404)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        if self.path == "/exec":
            self._send(exec_cell(body.get("code", ""), int(body.get("timeout", 60))))
        elif self.path == "/reset":
            reset()
            self._send({"ok": True})
        else:
            self._send({"error": "unknown endpoint"}, 404)

    def log_message(self, fmt, *args):            # default logger breaks on Unix sockets (no client IP)
        sys.stderr.write(f"{time.strftime('%H:%M:%S')} {fmt % args}\n")


if __name__ == "__main__":
    reset()
    threading.Thread(target=idle_watchdog, daemon=True).start()
    threading.Thread(target=storage_watchdog, daemon=True).start()
    SOCKET.unlink(missing_ok=True)
    with socketserver.UnixStreamServer(str(SOCKET), Handler) as server:   # single-threaded = one cell at a time
        print(f"exec server listening on {SOCKET}", flush=True)
        server.serve_forever()
