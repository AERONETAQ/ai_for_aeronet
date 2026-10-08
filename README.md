# ai_for_aeronet
Agent that can do autonomous, scientifically correct data analysis on AERONET level 2 datasets.

## Layout

```
config/config.yaml   every setting: folders, keep_turns, model, limits, sandbox, container limit, terminal verbose
src/                 notebook 09 as a package (same code, one module per notebook section) + the terminal
  conversation/      store (SQLite), sandbox state, context (what the model sees), manage (new/load/delete/list)
  tools/             run_python, view_figure, kernel_state, reset_kernel · list_sites, describe_columns · fetch_turn
  skills/            one markdown file per skill; the number prefix is the order in the system prompt
  prompt/            rules, data dictionary, the system-prompt builder
  agent/             Turn schema + model + agent (build), ask() (run), token check (tokens)
  terminal/          python -m src.terminal
sandbox/             the docker image (Dockerfile, exec_server.py, download_natural_earth.py: offline Natural Earth
                     shapes for cartopy maps) and its host-side client (sandbox.py)
notebooks/           01 data download … 09 agent with long conversations (the terminal is 09 moved into src/)
DATA/                the parquet (gitignored)
conversation_data/   one folder per conversation = that sandbox's /workspace, plus agent_turns.sqlite (gitignored)
```

## Run the terminal

```
conda activate chatbot            # the env with pydantic-ai, rich, pyyaml
cd ai_for_aeronet
python -m src.terminal
```

`/new <name>` creates a conversation (folder + docker container of that name) and starts its sandbox,
`/load <name>` opens one, starts its sandbox and shows its last `keep_turns` turns, `/help` lists everything else.
A question is any line that does not start with `/`. The terminal says when a sandbox is being set up, when it was
left running, and when the one of the last turn is gone (idle stop, crash, `/stop`): then the variables are lost,
the files are kept, and the model is told with the next question.
Figures are not drawn in the terminal: the answer names each file's path on this machine, open it yourself.

**Several conversations at once:** open another terminal window, run the same three lines, `/new` or `/load`
another conversation. `max_running_containers` in the config caps how many sandboxes may be up at once across all
terminals; a terminal that would exceed it is told which conversations hold the slots (`/stop` in one of them frees
it). Do not open the same conversation in two terminals: both would write to the same kernel and turn list.

`terminal.verbose` in the config is a set of on/off flags: `steps` and `step_tokens` (one line per step and its
tokens), `tool_calls` (every tool call and result, the notebook's full print), and under the answer `summary`,
`kept_variables`, `files`, `turn_tokens`, `conversation_cost`. `/verbose <flag>` flips one for the session.

**A local model (LM Studio, Ollama, vLLM):** in the config set `model.provider: openai-compatible`,
`base_url: http://localhost:1234/v1`, `model_id` to the model name the server shows, and `limits.cost_limit: null`
(no prices for local models). `src/agent/build.py make_model()` is the only code that knows the provider. The
model must support tool calling: the tools and the final answer are tool calls.

Another config file: `AERONET_CONFIG=/path/to/other.yaml python -m src.terminal`.
