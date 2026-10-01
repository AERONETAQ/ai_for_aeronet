"""Conversations: new, load, delete, list. A conversation name is its folder and its docker container name.

Neither create() nor load() starts the sandbox: the terminal does that right after (app.ensure_sandbox), so it
can tell the user what is happening. create() checks the container limit first, so a terminal that would exceed
max_running_containers is refused before anything is made.
"""
import re
import shutil

import sandbox as sb

from .. import config
from . import current
from .store import DB
from .sandbox_state import check_slot, running_sandboxes

NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]+$")    # what docker accepts as a container name


def exists(name):
    """True when the conversation has a folder or stored turns."""
    folder = (config.CONV_DIR / name).is_dir()
    rows = DB.execute("SELECT 1 FROM turns WHERE conversation = ? LIMIT 1", (name,)).fetchone()
    return folder or rows is not None


def create(name):
    """New conversation: check the name and the container limit, make its folder, switch to it."""
    if not NAME.match(name):
        raise ValueError(f"'{name}': use letters, digits, _ . - (at least 2 characters, starting with a letter or digit)")
    if exists(name):
        raise ValueError(f"'{name}' already exists (folder {config.CONV_DIR / name}); /load {name} instead")
    check_slot()
    (config.CONV_DIR / name).mkdir(parents=True)
    current.use(name)


def load(name):
    """Switch to an existing conversation."""
    if not exists(name):
        raise ValueError(f"no conversation '{name}'; /list shows them, /new {name} creates it")
    current.use(name)


def delete(name):
    """Stop the sandbox, delete the folder (files, figures) and every stored turn."""
    if not exists(name):
        raise ValueError(f"no conversation '{name}'")
    sb.stop(name)
    shutil.rmtree(config.CONV_DIR / name, ignore_errors=True)
    DB.execute("DELETE FROM turns WHERE conversation = ?", (name,))
    DB.commit()
    if current.ID == name:
        current.use(None)


def list_all():
    """One dict per conversation: name, turns, cost, last question time, sandbox running or not."""
    names = {p.name for p in config.CONV_DIR.iterdir() if p.is_dir()}
    stats = {}
    for r in DB.execute("SELECT conversation, COUNT(*) AS turns, SUM(cost_usd) AS cost, MAX(asked) AS last "
                        "FROM turns GROUP BY conversation"):
        stats[r["conversation"]] = r
    up = set(running_sandboxes())
    rows = []
    for name in sorted(names | stats.keys()):
        s = stats.get(name)
        rows.append({"name":    name,
                     "turns":   s["turns"] if s else 0,
                     "cost":    (s["cost"] or 0) if s else 0,
                     "last":    (s["last"] or "") if s else "",
                     "running": name in up})
    return rows
