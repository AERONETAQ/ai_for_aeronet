"""Section 1 · Store.

One SQLite file, one table `turns`, one row per question. This file is the conversation's long-term memory:
it is written once at the end of every question and read at the start of the next one. Three SQL statements
here: create the table, insert a row, select all rows of this conversation (manage.py adds list and delete).
Everything else is plain Python on that list of rows.

- all_turns(): every row, oldest first, stopped turns included (for cost and the last sandbox id).
- recent_turns(): the last KEEP_TURNS rows with status = 'ok'. These reach the model in full.
- older_turns(): the finished rows before those. The model gets one line each (model_summary) and can ask
  for the whole turn with fetch_turn.

Tokens. Pydantic AI adds up every model call of the turn. Its input_tokens is everything sent to the model,
cached or not, so the parts add up exactly:
    input_tokens  = uncached_input + cache_read + cache_write
    output_tokens = visible text and tool calls + reasoning_tokens
reasoning_tokens is NULL when the provider does not report it. agent/tokens.py re-adds the tokens call by
call from the stored messages and checks they match this row.
"""
import sqlite3

import pandas as pd

from .. import config
from . import current

config.CONV_DIR.mkdir(parents=True, exist_ok=True)
DB = sqlite3.connect(config.DB_FILE, check_same_thread=False)   # fetch_turn reads it from the thread Pydantic AI runs tools in
DB.row_factory = sqlite3.Row          # a row behaves like a dict: row["question"]

DB.execute("""
CREATE TABLE IF NOT EXISTS turns (
    conversation     TEXT,
    turn             INTEGER,  -- 1, 2, 3 ... within the conversation
    asked            TEXT,     -- UTC time of the question
    status           TEXT,     -- ok | stopped (a usage limit ended the turn)
    question         TEXT,
    answer           TEXT,     -- NULL when stopped
    summary          TEXT,     -- one line: tools used, files written (read off the tool calls, no model)
    model_summary    TEXT,     -- one line written by the model: what was asked and what came out (the index line)
    variables        TEXT,     -- JSON list of {name, meaning}: what the model kept in the kernel
    sandbox          TEXT,     -- id of the docker container the turn ran on (new id = sandbox restarted)
    restart_note     TEXT,     -- what the model was told about a restart before this turn, else NULL
    requests         INTEGER,  -- model calls
    tool_calls       INTEGER,  -- tool executions
    input_tokens     INTEGER,  -- all input  = uncached_input + cache_read + cache_write
    uncached_input   INTEGER,
    cache_read       INTEGER,
    cache_write      INTEGER,
    output_tokens    INTEGER,  -- all output, reasoning included
    reasoning_tokens INTEGER,  -- part of output_tokens; NULL if not reported
    cost_usd         REAL,
    messages         TEXT,     -- the full trace: every message of the turn as Pydantic AI JSON
    PRIMARY KEY (conversation, turn)
)""")
# the table may already exist from notebook 07/08 without the new column: add it once
if "model_summary" not in [col[1] for col in DB.execute("PRAGMA table_info(turns)")]:
    DB.execute("ALTER TABLE turns ADD COLUMN model_summary TEXT")


def all_turns():
    """Every stored turn of this conversation, oldest first."""
    return DB.execute("SELECT * FROM turns WHERE conversation = ? ORDER BY turn", (current.ID,)).fetchall()


def recent_turns():
    """The last KEEP_TURNS turns that finished (status ok). Stopped turns are never shown to the model."""
    finished = [t for t in all_turns() if t["status"] == "ok"]
    return finished[-config.KEEP_TURNS:]


def older_turns():
    """The finished turns before the recent ones: the model sees them as one index line each."""
    finished = [t for t in all_turns() if t["status"] == "ok"]
    return finished[:-config.KEEP_TURNS]


def save_turn(row):
    """row = {column: value}. Adds the conversation id and the next turn number, inserts it, returns the number."""
    row = {"conversation": current.ID, "turn": len(all_turns()) + 1, **row}
    columns = ", ".join(row.keys())
    placeholders = ", ".join(["?"] * len(row))
    DB.execute(f"INSERT INTO turns ({columns}) VALUES ({placeholders})", list(row.values()))
    DB.commit()
    return row["turn"]


def token_columns(usage):
    """Pydantic AI usage (of a whole turn, or of one model call) -> the token and cost columns of the table."""
    return {
        "input_tokens":     usage.input_tokens,
        "uncached_input":   usage.input_tokens - usage.cache_read_tokens - usage.cache_write_tokens,
        "cache_read":       usage.cache_read_tokens,
        "cache_write":      usage.cache_write_tokens,
        "output_tokens":    usage.output_tokens,
        "reasoning_tokens": usage.details.get("reasoning_tokens"),      # None if not reported
        "cost_usd":         float(usage.cost) if usage.cost is not None else None,
    }


def conversation_cost():
    """USD spent so far in this conversation, stopped turns included."""
    total = 0.0
    for t in all_turns():
        total += t["cost_usd"] or 0
    return total


def show_turns():
    """The table without the long columns (answer, messages)."""
    columns = ["turn", "asked", "status", "question", "model_summary", "summary", "variables", "sandbox", "restart_note",
               "requests", "tool_calls", "input_tokens", "uncached_input", "cache_read", "cache_write",
               "output_tokens", "reasoning_tokens", "cost_usd"]
    rows = [{c: t[c] for c in columns} for t in all_turns()]
    return pd.DataFrame(rows, columns=columns)
