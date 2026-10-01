"""Section 4 · The tools that touch the sandbox.

run_python returns a list when the cell saved PNGs: the usual text, then for each PNG one line
`[image: name, WxH px, ≈N tokens]` followed by the image itself. At most MAX_IMAGES_PER_CALL images per cell;
the others are named so the model can view_figure one. view_figure(name) returns one PNG from /workspace the
same way. image_for_model(name) builds the label line + image pair for both; the token estimate is a pixel fit
measured on GPT-5.6 Luna on 2026-09-30 (≈ 190 + 0.94 per 1000 px).
"""
import json

from PIL import Image as PILImage
from pydantic_ai.messages import BinaryImage
import sandbox as sb

from .. import config
from ..conversation import current
from ..conversation.sandbox_state import start_sandbox_if_needed


def image_for_model(name):
    """One PNG from /workspace as the model receives it: a label line, then the image itself."""
    path = current.WORKSPACE / name
    width, height = PILImage.open(path).size
    tokens = int(190 + 0.94 * width * height / 1000)      # fitted on Luna 2026-09-30; the API does not report image tokens
    label = f"[image: {name}, {width}x{height} px, ≈{tokens} tokens]"
    return [label, BinaryImage.from_path(path)]


def run_python(code: str, timeout: int = 60) -> str | list:
    '''Run Python code in this conversation's sandbox (a persistent IPython kernel) and return what happened.
    Pre-imported: numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns.
    DATA = path of the AERONET AOD Level 2 daily parquet (read-only; Always read a column subset, the full table is ~1 GB; The system where the code executes is very lightweight).
    Variables persist between calls. No network. 2 GB RAM, 2 CPUs.
    What comes back, like a notebook cell:
    - stdout: everything you print(); stderr: warnings.
    - result: the value of the last expression if it is not an assignment (a DataFrame comes back as shape, dtypes,
      head and tail). Assign to a variable to suppress it.
    - stdout, stderr and result are each cut to 4000 characters (middle removed, marked "[N chars clipped]").
      Show only what you need: a small slice, .to_string() on a few rows, or aggregate first. Never print a whole
      table; save it as CSV under /workspace/ and report the file name.
    - Figures: save them yourself with fig.savefig('/workspace/<descriptive_name>.png'); any figure left open is
      auto-saved as fig_NNN.png. No plt.show(). All PNG names written by the cell are returned under figures,
      and the images themselves are shown to you right after (the first 4 per call): look at them for double checking or verification.
    - new/changed variables with type and shape, files written, elapsed time and memory.
    Write any export (parquet, csv, png) under /workspace/.'''
    start_sandbox_if_needed()
    r = sb.exec_code(current.ID, code, timeout)
    out = []
    if r.get("stdout"):       out.append("stdout:\n" + r["stdout"].rstrip())
    if r.get("stderr"):       out.append("stderr:\n" + r["stderr"].rstrip())
    if r.get("error"):        out.append("ERROR: " + r["error"])
    if r.get("result"):       out.append("result:\n" + r["result"])
    if r.get("figures"):      out.append("figures saved: " + ", ".join(r["figures"]))
    if r.get("new_files"):    out.append("files written: " + ", ".join(r["new_files"]))
    if r.get("vars_new"):     out.append(f"new variables: {r['vars_new']}")
    if r.get("vars_changed"): out.append(f"changed variables: {r['vars_changed']}")
    if "elapsed_s" in r:      out.append(f"[{r['elapsed_s']} s | memory used {r['rss_mb']} of {r.get('memory_limit_mb')} MB]")
    text = "\n".join(out) or "(no output)"

    figures = r.get("figures") or []
    if not figures:
        return text

    # the text, then the images the cell saved (at most MAX_IMAGES_PER_CALL): the model sees them in this result
    content = [text]
    for name in figures[:config.MAX_IMAGES_PER_CALL]:
        content += image_for_model(name)
    not_shown = figures[config.MAX_IMAGES_PER_CALL:]
    if not_shown:
        content.append(f"[{len(not_shown)} more figures saved but not shown: {', '.join(not_shown)}; view_figure(name) shows one]")
    return content


def view_figure(name: str) -> str | list:
    '''Look at one PNG from /workspace, e.g. a figure made in an earlier question (earlier answers name their files).
    Do NOT use it for figures made in this question: every run_python result already shows you the PNGs it saved,
    and once you have seen an image it stays in front of you. Use it only when the question depends on what an
    older figure shows and the earlier answer does not already say it. Each image costs a few hundred tokens.'''
    name = name.replace("sandbox:", "").replace("/workspace/", "")    # accept the full path too
    if not name.lower().endswith(".png"):
        return f"{name}: only PNG files can be viewed"
    if not (current.WORKSPACE / name).exists():
        return f"{name}: no such file in /workspace (check the name in the earlier answer). The file could also have been deleted! or maybe check the spelling of the name."
    return image_for_model(name)


def kernel_state() -> str:
    '''Variables (type and shape), files in /workspace and memory use of this conversation's sandbox.'''
    return json.dumps(sb.state(current.ID), indent=1)


def reset_kernel() -> str:
    '''Delete all variables and open figures. Files in /workspace are kept.'''
    sb.reset(current.ID)
    return "kernel reset: no variables"
