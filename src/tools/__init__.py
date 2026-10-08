"""Section 4 · Tools. Eight tools in four files (notebook 09's, minus kernel_state and reset_kernel, plus three
about places and tables):

sandbox_tools.py   run_python, view_figure                                (touch the sandbox)
data_tools.py      list_sites, describe_columns                          (host-side, read the parquet tables; data-specific)
geo_tools.py       geocode (needs the internet), nearest_sites, site_coverage   (host-side; geocode is VAYU v2's)
history_tools.py   fetch_turn                                            (reads SQLite)
"""
from pydantic_ai import Tool

from .sandbox_tools import run_python, view_figure
from .data_tools import list_sites, describe_columns
from .geo_tools import geocode, nearest_sites, site_coverage
from .history_tools import fetch_turn

TOOLS = [Tool(run_python,   sequential=True),       # never two code calls at once on one kernel
         Tool(describe_columns, sequential=True),    # first call builds the per-site counts once; never two at a time
         Tool(geocode,      sequential=True),       # one request per second to Nominatim: never two calls at once
         Tool(site_coverage, sequential=True),      # first call reads the site list of every table once
         list_sites, nearest_sites, view_figure, fetch_turn]
