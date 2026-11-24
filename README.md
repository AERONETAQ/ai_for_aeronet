# ai_for_aeronet
Agent that can do autonomous, scientifically correct data analysis on AERONET datasets: solar AOD, aerosol inversion products
(hybrid and almucantar scans) and lunar night-time AOD, at Level 2.0 and Level 1.5, as monthly means, daily means
and all points (20 tables).

## Layout

```
config/config.yaml   every setting: folders and the 20 data tables, keep_turns, model, limits, sandbox, container limit, terminal verbose
src/                 notebook 09 as a package (same code, one module per notebook section) + the terminal
  conversation/      store (SQLite), sandbox state, context (what the model sees), manage (new/load/delete/list)
  tools/             run_python, view_figure · list_sites, describe_columns (dataset=...) · geocode (VAYU v2's, Nominatim),
                     nearest_sites, site_coverage · fetch_turn
  skills/            one markdown file per skill; the number prefix is the order in the system prompt
  prompt/            rules, data dictionary (the 20 tables), the system-prompt builder
  agent/             Turn schema + model + agent (build), ask() (run), token check (tokens)
  terminal/          python -m src.terminal
sandbox/             the docker image (Dockerfile, exec_server.py, download_natural_earth.py: offline Natural Earth
                     shapes for cartopy maps) and its host-side client (sandbox.py)
notebooks/           01 data download … 09 agent with long conversations (the terminal is 09 moved into src/)
  process_data/      05 converts any AERONET product (a file or a folder of station files) into one parquet in
                     DATA/PROCESSED/: uncomment one product, run, repeat for each of the 20 tables. 01–04 are the
                     earlier one-notebook-per-table versions (they also download the archives)
DATA/                RAW/ the extracted station files, PROCESSED/ the 20 parquet tables (gitignored); PROCESSED/ is
                     mounted read-only at /data in the sandbox (DATA, DATA_L15, DATA_MONTHLY, DATA_LUNAR, DATA_INV, DATA_ALM ... in the kernel)
conversation_data/   one folder per conversation = that sandbox's /workspace, plus agent_turns.sqlite (gitignored)
```

## Run the terminal

```
conda activate chatbot            # the env with pydantic-ai, rich, pyyaml
cd ai_for_aeronet
python -m src.terminal
```

The sandbox image builds itself on the first start and rebuilds whenever a file in `sandbox/` changed since the
image was built (its build hash is a label on the image), so a `git pull` needs no manual `docker build`. A start
refuses to run while one of the 20 tables is missing from `DATA/PROCESSED/` and names the notebook that writes it.

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
