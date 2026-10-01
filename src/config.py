"""Reads config/config.yaml once. Every other module takes its settings from here, under the names notebook 09 used.

Another config file: AERONET_CONFIG=/path/to/other.yaml python -m src.terminal
"""
import os
from pathlib import Path

import yaml
import sandbox as sb

from . import PROJECT_ROOT

CONFIG_FILE = Path(os.environ.get("AERONET_CONFIG", PROJECT_ROOT / "config" / "config.yaml"))
_cfg = yaml.safe_load(CONFIG_FILE.read_text())

# folders (a relative path starts at the project folder; an absolute one is taken as is)
CONV_DIR = PROJECT_ROOT / _cfg["conversation_dir"]     # one sub-folder per conversation = the sandbox's /workspace
PARQUET  = PROJECT_ROOT / _cfg["data_file"]            # mounted read-only at /data/aeronet.parquet
DB_FILE  = CONV_DIR / _cfg["db_file"]
sb.CONV_DIR, sb.PARQUET = CONV_DIR, PARQUET            # the sandbox client has its own defaults; the config wins

# the conversation
KEEP_TURNS          = _cfg["keep_turns"]
CONV_COST_LIMIT     = _cfg["conv_cost_limit"]
SHOW_FIGURES        = _cfg["show_figures"]
MAX_IMAGES_PER_CALL = _cfg["max_images_per_call"]
MAX_SITE_ROWS       = _cfg["max_site_rows"]

# the model
PROVIDER         = _cfg["model"]["provider"]          # bedrock-mantle | openai-compatible
REGION           = _cfg["model"]["region"]
BASE_URL         = _cfg["model"]["base_url"].format(region=REGION)
API_KEY          = os.path.expandvars(str(_cfg["model"]["api_key"]))   # ${OPENAI_API_KEY} -> the environment variable
MODEL_ID         = _cfg["model"]["model_id"]
REASONING_EFFORT = _cfg["model"]["reasoning_effort"]
MAX_TOKENS       = _cfg["model"]["max_tokens"]
PROMPT_CACHE_KEY = _cfg["model"]["prompt_cache_key"]
PRICES           = _cfg["model"].get("prices") or {}  # {input, cache_read, cache_write, output}: USD per M tokens, None = built-in

# one question
LIMITS       = _cfg["limits"]            # request_limit, tool_calls_limit, total_tokens_limit, cost_limit
TOOL_TIMEOUT = _cfg["tool_timeout"]
RETRIES      = _cfg["retries"]

# the sandbox
SANDBOX                = _cfg["sandbox"]  # memory, cpus, workspace_gb, idle_minutes -> sb.start()
MAX_RUNNING_CONTAINERS = _cfg["max_running_containers"]

# the terminal
VERBOSE = _cfg["terminal"]["verbose"]     # {steps, step_tokens, tool_calls, summary, kept_variables, files, turn_tokens, conversation_cost}
