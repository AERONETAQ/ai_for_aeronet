"""
Host-side client for the sandbox: start/stop a container per conversation and call
the 4 endpoints of exec_server.py (exec / state / reset / env) over its Unix socket.

Folders:  <repo>/conversation_data/<conversation_id>/  = the container's /workspace  (gitignored)
Container name = conversation_id.
"""
import http.client, json, os, socket, subprocess, time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARQUET      = PROJECT_ROOT / "DATA" / "PROCESSED" / "AERONET_AOD_L2_Daily_V3.parquet"
CONV_DIR     = PROJECT_ROOT / "conversation_data"     # one sub-folder per conversation (gitignored)
IMAGE        = "aeronet-sandbox"


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
    subprocess.run(cmd, check=True, capture_output=True, text=True)
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


class UnixHTTP(http.client.HTTPConnection):                          # HTTP over the socket file in the workspace
    def __init__(self, path, timeout):
        super().__init__("localhost", timeout=timeout)
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


def call(conv_id, endpoint, payload=None, timeout=30):
    conn = UnixHTTP(str(CONV_DIR / conv_id / "exec.sock"), timeout)
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
