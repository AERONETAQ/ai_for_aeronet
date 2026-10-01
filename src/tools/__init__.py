"""Section 4 · Tools. The seven tools of notebook 09, in three files:

sandbox_tools.py   run_python, view_figure, kernel_state, reset_kernel   (touch the sandbox)
data_tools.py      list_sites, describe_columns                          (host-side, read the parquet; data-specific)
history_tools.py   fetch_turn                                            (reads SQLite)
"""
from pydantic_ai import Tool

from .sandbox_tools import run_python, view_figure, kernel_state, reset_kernel
from .data_tools import list_sites, describe_columns
from .history_tools import fetch_turn

TOOLS = [Tool(run_python,   sequential=True),       # never two code calls at once on one kernel
         Tool(reset_kernel, sequential=True),
         Tool(describe_columns, sequential=True),    # first call builds the per-site counts once; never two at a time
         kernel_state, list_sites, view_figure, fetch_turn]
