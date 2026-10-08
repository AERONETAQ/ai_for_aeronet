"""Section 2 · Sandbox and its variables.

This is the "memory" part. Three facts drive all of it:
- Variables live in the sandbox, files live on disk. When the sandbox stops (idle minutes, memory or storage
  limit, sb.stop) every variable is gone; the files in /workspace stay.
- Every start of the sandbox is a new docker container with a new id. Each turn stores the id it ran on
  (`sandbox` column). "Did the sandbox restart since the last turn?" is just "is the id different now?",
  and only turns with the current id can have left variables behind.
- The model says which variables to keep. Every answer ends with kept_variables (name + one-line meaning).
  After each turn, the variables named by any of the recent turns on this sandbox stay, all others are deleted.

New here: running_sandboxes() and check_slot(), the limit on how many sandboxes of this project may be up at
the same time (config max_running_containers), counted across every terminal. check_slot() is the one added line
in start_sandbox_if_needed(); the functions print nothing, the terminal narrates (app.ensure_sandbox).
"""
import json
import subprocess

import sandbox as sb

from .. import config
from . import current
from .store import all_turns, recent_turns

LAST_STOP_REASON = "unknown"      # why the sandbox was last found stopped; only used in the restart note


def sandbox_id():
    """Short docker id of the running sandbox, "" if none. Changes on every start."""
    out = subprocess.run(["docker", "ps", "-q", "--filter", f"name=^{current.ID}$"],
                         capture_output=True, text=True)
    return out.stdout.strip()


def running_sandboxes():
    """Names of every running sandbox of this project, whatever conversation or terminal started it."""
    out = subprocess.run(["docker", "ps", "--filter", f"ancestor={sb.IMAGE}", "--format", "{{.Names}}"],
                         capture_output=True, text=True)
    return out.stdout.split()


def check_slot():
    """Refuse one more sandbox when max_running_containers are already up (in any terminal)."""
    up = running_sandboxes()
    if len(up) >= config.MAX_RUNNING_CONTAINERS:
        raise RuntimeError(f"{len(up)} sandbox(es) already running ({', '.join(up)}); the limit is "
                           f"{config.MAX_RUNNING_CONTAINERS} (max_running_containers in config.yaml). "
                           "Stop one with /stop in its terminal, or raise the limit.")


NOTEBOOK_OF = {"aod_l2": "01", "aod_l15": "02", "inv": "03", "lunar": "04"}   # which notebooks/process_data/ notebook writes each table


def check_tables():
    """Every table of config data_files must exist before a sandbox mounts DATA/PROCESSED: a missing one would
    only surface later, inside a cell, as a FileNotFoundError."""
    missing = [f"{path.name} (run notebooks/process_data/{NOTEBOOK_OF.get(name, '?')}_*.ipynb)"
               for name, path in config.DATA_FILES.items() if not path.exists()]
    if missing:
        raise RuntimeError("tables missing from DATA/PROCESSED: " + "; ".join(missing))


def start_sandbox_if_needed():
    """Start the sandbox when it is not running, remembering why the previous one stopped."""
    global LAST_STOP_REASON
    if sb.running(current.ID):
        return
    check_tables()
    check_slot()
    killed_file = current.WORKSPACE / "_killed.txt"          # the sandbox writes its reason here when it stops itself
    if killed_file.exists():
        LAST_STOP_REASON = killed_file.read_text().strip()
    else:
        LAST_STOP_REASON = "no reason recorded: memory limit, host restart or stopped by hand"
    sb.start(current.ID, **config.SANDBOX)                   # deletes _killed.txt, so it is read first


def sandbox_restarted():
    """True when the last stored turn ran on another sandbox than the one up now."""
    turns = all_turns()
    if not turns:
        return False                                   # first question: nothing to have lost
    return turns[-1]["sandbox"] != sandbox_id()


def variable_meanings():
    """{name: meaning} from kept_variables of the recent turns that ran on the sandbox up now; later turns win."""
    current_id = sandbox_id()
    meanings = {}
    for t in recent_turns():
        if t["sandbox"] != current_id:
            continue                                   # ran on an older sandbox: its variables are gone
        for v in json.loads(t["variables"]):
            meanings[v["name"]] = v["meaning"]
    return meanings


def state_block(restart_note=None):
    """The text put on top of every question: what the sandbox holds right now."""
    state = sb.state(current.ID)
    meanings = variable_meanings()
    lines = ["### sandbox state now"]

    if restart_note:
        lines.append(f"kernel: {restart_note}")

    if state["vars"]:
        lines.append("variables (name: type — what it holds):")
        for name, vtype in state["vars"].items():
            lines.append(f"  {name}: {vtype} — {meanings.get(name, 'not described')}")
    else:
        lines.append("variables: none")

    lines.append(f"memory used: {state['rss_mb']} of {state['memory_limit_mb']} MB; "
                 f"storage used: {state['workspace_mb']} of {state['workspace_cap_mb']} MB in /workspace")
    return "\n".join(lines)


RELEASE_MEMORY = """%reset -f out
__import__('gc').collect()
__import__('pyarrow').default_memory_pool().release_unused()
__import__('ctypes').CDLL('libc.so.6').malloc_trim(0)"""


def cleanup_kernel():
    """After a finished turn: keep the variables recent turns named in kept_variables, delete the rest."""
    keep = variable_meanings()
    live = sb.state(current.ID)["vars"]
    kept    = [name for name in live if name in keep]
    deleted = [name for name in live if name not in keep]
    # del + gc alone give nothing back to the OS (measured 2026-09-30: 636 MB before and after). Three more steps
    # bring a turn back to ~280 MB: IPython's Out cache holds every value a cell returned as its last expression,
    # pyarrow's pool keeps freed buffers for reuse, and libc keeps its arenas. __import__(...) instead of import,
    # so no new variable appears in the kernel.
    code = ("del " + ", ".join(deleted) + "\n" if deleted else "") + RELEASE_MEMORY
    sb.exec_code(current.ID, code)
    return kept, deleted
