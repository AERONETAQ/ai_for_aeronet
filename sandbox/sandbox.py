"""
Host-side client for the sandbox: start/stop a container per conversation and call
the 4 endpoints of exec_server.py (exec / state / reset / env) over its Unix socket.

Folders:  <repo>/conversation_data/<conversation_id>/  = the container's /workspace  (gitignored)
Container name = conversation_id.
"""
import http.client, json, os, socket, subprocess, threading, time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARQUET      = PROJECT_ROOT / "DATA" / "PROCESSED" / "AERONET_AOD_L2_Daily_V3.parquet"
CONV_DIR     = PROJECT_ROOT / "conversation_data"     # one sub-folder per conversation (gitignored)
IMAGE        = "aeronet-sandbox"


def _folder_bytes(folder):
    total = 0
    for root, _, names in os.walk(folder):
        for n in names:
            total += os.lstat(os.path.join(root, n)).st_size    # lstat: a symlink counts as itself, never as its target
    return total


def _alive(container_id):
    out = subprocess.run(["docker", "ps", "-q", "--no-trunc", "--filter", f"id={container_id}"], capture_output=True, text=True)
    return out.stdout.strip() != ""


def _host_storage_guard(conv_id, container_id, cap):
    """Backstop for the storage watchdog inside exec_server.py. That one runs in the same process as the model's
    code, which could in principle switch it off; this one runs in the terminal's own process, outside the
    container, once a second, for as long as the container it was started for is up."""
    ws = CONV_DIR / conv_id
    tick = 0
    while True:
        time.sleep(1)
        tick += 1
        if tick % 10 == 0 and not _alive(container_id):                 # idle stop, OOM, stop(): nothing left to guard
            return
        used = _folder_bytes(ws)
        if used <= cap:
            continue
        reason = f"storage cap exceeded: /workspace went over {cap/1e9:g} GB. Sandbox killed by the host"
        (ws / "_killed.txt").write_text(reason)                          # written BEFORE the kill: exec_code reads it the moment the socket dies
        stop(conv_id)                                                    # docker rm -f: immediate, nothing inside can block it
        used = _folder_bytes(ws)                                         # measure again now that nothing else writes or deletes
        deleted = []
        keep = {ws / "exec.sock", ws / "_killed.txt"}
        for p in sorted((p for p in ws.rglob("*") if p.is_file() and not p.is_symlink() and p not in keep),
                        key=lambda p: p.lstat().st_mtime, reverse=True):  # newest first, like exec_server
            if used <= cap:
                break
            used -= p.lstat().st_size
            p.unlink()
            deleted.append(p.name)
        (ws / "_killed.txt").write_text(f"{reason}; newest files deleted to get back under the cap: {deleted}")
        return


def start(conv_id, memory="2g", cpus=2, workspace_gb=1, idle_minutes=60):
    """docker run with every limit; returns /env once the server answers."""
    ws = CONV_DIR / conv_id
    ws.mkdir(parents=True, exist_ok=True)
    (ws / "_killed.txt").unlink(missing_ok=True)
    stop(conv_id)                                                    # never two containers for one conversation
    if subprocess.run(["docker", "image", "inspect", IMAGE], capture_output=True).returncode != 0:
        print(f"building the {IMAGE} image (first run only, a few minutes) ...")
        subprocess.run(["docker", "build", "-t", IMAGE, str(Path(__file__).parent)], check=True)
    cmd =["docker", "run", "-d", "--rm", "--name", conv_id,
        "--network", "none",                                         # no internet, no LAN
        "--memory", memory, "--memory-swap", memory,                 # RAM cap, no swap
        "--cpus", str(cpus),
        "--pids-limit", "256",                                       # no fork bombs
        "--read-only", "--tmpfs", "/tmp:size=256m",                  # image files can't be changed; /tmp is small
        "--ulimit", f"fsize={int(workspace_gb * 1e9)}",              # no single file above N GB (kernel enforced)
        "--cap-drop", "ALL",                                         # no privileges at all
        "--user", f"{os.getuid()}:{os.getgid()}",                    # files it writes are yours, not root's
        "-e", f"WORKSPACE_GB={workspace_gb}", "-e", f"IDLE_MINUTES={idle_minutes}",
        "-v", f"{PARQUET}:/data/aeronet.parquet:ro",                 # the data, read-only
        "-v", f"{ws}:/workspace",                                    # the only writable place (+ the socket)
        IMAGE]
    container_id = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip()
    threading.Thread(target=_host_storage_guard, args=(conv_id, container_id, int(workspace_gb * 1e9)), daemon=True).start()
    for _ in range(100):                                             # wait until the server answers
        try:
            return env(conv_id)
        except OSError:
            time.sleep(0.2)
    # did not come up (and --rm already removed it): run it once more in the foreground to see why
    try:
        r = subprocess.run([x for x in cmd if x not in ("-d", "--rm")], capture_output=True, text=True, timeout=10)
        raise RuntimeError(f"sandbox '{conv_id}' did not start:\n{r.stdout}{r.stderr}")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"sandbox '{conv_id}' starts but did not answer within 20 s")
    finally:
        stop(conv_id)


def stop(conv_id):
    subprocess.run(["docker", "rm", "-f", conv_id], capture_output=True)


def running(conv_id):
    out = subprocess.run(["docker", "ps", "-q", "--filter", f"name=^{conv_id}$"], capture_output=True, text=True)
    return out.stdout.strip() != ""


# class UnixHTTP(http.client.HTTPConnection):                          # HTTP over the socket file in the workspace
#     def __init__(self, path, timeout):
#         super().__init__("localhost", timeout=timeout)
#         self.path = path

#     def connect(self):
#         self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#         self.sock.settimeout(self.timeout)
#         self.sock.connect(self.path)

RELAY = r"""
import socket, sys, threading
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect('/workspace/exec.sock')

def upstream():
    # host -> server: forward whatever arrives on stdin
    while True:
        d = sys.stdin.buffer.read1(65536)
        if not d:
            break
        s.sendall(d)
    s.shutdown(socket.SHUT_WR)

threading.Thread(target=upstream, daemon=True).start()

# server -> host: forward responses to stdout until the server closes
while True:
    d = s.recv(65536)
    if not d:
        break
    sys.stdout.buffer.write(d)
    sys.stdout.buffer.flush()
"""


class DockerExecHTTP(http.client.HTTPConnection):
    """HTTP over the container's Unix socket, tunneled through `docker exec -i`.
    Works on Docker Desktop for Mac, where host -> container Unix sockets do not."""

    def __init__(self, container: str, timeout: float):
        super().__init__("localhost", timeout=timeout)
        self.container = container
        self.proc = None

    def connect(self):
        # One end of the pair becomes docker exec's stdin+stdout; the other is our "socket"
        ours, theirs = socket.socketpair()
        self.proc = subprocess.Popen(
            ["docker", "exec", "-i", self.container, "python", "-u", "-c", RELAY],
            stdin=theirs, stdout=theirs, stderr=subprocess.DEVNULL,
        )
        theirs.close()                 # the child process holds its own copy
        ours.settimeout(self.timeout)  # keeps the existing timeout semantics
        self.sock = ours

    def close(self):
        super().close()
        # Don't leave relay processes behind
        if self.proc and self.proc.poll() is None:
            self.proc.kill()
            self.proc.wait()
        self.proc = None


def call(conv_id, endpoint, payload=None, timeout=30):
    # conn = UnixHTTP(str(CONV_DIR / conv_id / "exec.sock"), timeout)
    conn = DockerExecHTTP(conv_id, timeout)

    if payload is None:                                              # GET: no body, the server never reads one
        conn.request("GET", endpoint)
    else:
        conn.request("POST", endpoint, body=json.dumps(payload), headers={"Content-Type": "application/json"})
    out = json.loads(conn.getresponse().read())
    conn.close()
    return out


# ── the 4 endpoints ──────────────────────────────────────────────────────────
def env(conv_id):   return call(conv_id, "/env")
def state(conv_id): return call(conv_id, "/state")
def reset(conv_id): return call(conv_id, "/reset", {})


def exec_code(conv_id, code, timeout=60):
    """Run one cell. Never raises: a dead container comes back as ok=False with an explanation."""
    try:
        return call(conv_id, "/exec", {"code": code, "timeout": timeout}, timeout=timeout + 10)
    except OSError:                                                  # socket refused / reset = container is gone
        killed = CONV_DIR / conv_id / "_killed.txt"                  # the server leaves its reason there ...
        reason = killed.read_text() if killed.exists() else "killed by the memory limit"   # ... except when the kernel OOM-kills it
        return {"ok": False, "error": f"sandbox '{conv_id}' is not running: {reason}. "
                                      f"All variables are lost, files are kept. start('{conv_id}') gives a fresh sandbox."}
