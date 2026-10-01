"""Notebook 09 (agent with long conversations) as a package, plus a terminal.

notebook section -> module
  1 store                    conversation/store.py
  2 sandbox and variables    conversation/sandbox_state.py
  3 what the model sees      conversation/context.py
  4 tools                    tools/
  5 skills                   skills/  (one markdown file per skill)
  6 system prompt            prompt/
  7 model and agent          agent/build.py
  8 ask()                    agent/run.py
  10 check the tokens        agent/tokens.py
  new: conversations         conversation/manage.py  (new / load / delete / list, container limit)
  new: terminal              terminal/               (python -m src.terminal)
Every setting comes from config/config.yaml through config.py.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")    # no Pydantic AI banner on the first run (cell 1 of the notebook)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "sandbox"))      # `import sandbox as sb`, as the notebooks do
sys.modules.pop("sandbox", None)   # from the project folder the sandbox/ directory itself imports as an empty package; drop it
