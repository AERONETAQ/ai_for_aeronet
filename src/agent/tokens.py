"""Section 10 · Check the tokens.

Every model response in the stored trace carries its own usage. calls_table(turn) lists them one call per row
and adds them up; check_tokens(turn) compares that sum with the turn's row in the table. They must be equal.
Two more columns per call: images = how many images were in the model's context for that call (an image stays
in the context for the rest of the question), image_tokens_est = their estimated token cost, summed from the
`[image: ..., ≈N tokens]` lines. input_tokens already contains them; the estimate only shows their share.
"""
import re

import pandas as pd
from pydantic_ai.messages import ModelMessagesTypeAdapter, ModelRequest, ModelResponse, ToolReturnPart

from ..conversation.store import all_turns, token_columns
from ..conversation.context import tool_text

TOKEN_COLUMNS = ["input_tokens", "uncached_input", "cache_read", "cache_write", "output_tokens", "reasoning_tokens"]


def load_messages(turn):
    row = all_turns()[turn - 1]
    return ModelMessagesTypeAdapter.validate_json(row["messages"])


def calls_table(turn):
    """One row per model call of a stored turn, read from its trace, with the images in context at that call."""
    rows = []
    images, image_tokens = 0, 0                             # grow as image lines appear, never shrink within a turn
    for message in load_messages(turn):
        if isinstance(message, ModelRequest):
            for part in message.parts:
                if isinstance(part, ToolReturnPart):
                    for estimate in re.findall(r"\[image: .*?≈(\d+) tokens\]", tool_text(part)):
                        images += 1
                        image_tokens += int(estimate)
        if isinstance(message, ModelResponse):
            columns = token_columns(message.usage)          # same arithmetic as the stored row
            row = {c: columns[c] for c in TOKEN_COLUMNS + ["cost_usd"]}
            row["images"], row["image_tokens_est"] = images, image_tokens
            rows.append(row)
    return pd.DataFrame(rows, index=pd.RangeIndex(1, len(rows) + 1, name="call"))


def check_tokens(turn):
    """Add up the model calls of a stored turn and compare with the numbers in its row."""
    calls  = calls_table(turn)
    stored = all_turns()[turn - 1]
    for c in TOKEN_COLUMNS + ["cost_usd"]:
        summed = sum(v or 0 for v in calls[c])              # None (not reported) counts as 0
        verdict = "ok" if abs(summed - (stored[c] or 0)) < 1e-9 else "MISMATCH"
        print(f"  {c:17} sum of {len(calls)} calls: {summed:>10.6g}   stored: {stored[c]!s:>10}   {verdict}")
