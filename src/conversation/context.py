"""Section 3 · What the model sees.

History. history_for_model() starts with the cache breakpoint, then the index of the older_turns() (one line
each: `turn N: <model_summary> | files: ...`), then each of the recent_turns() as two messages: the question
(prefixed with its turn number) and the answer with one extra line `[this turn did] tools: run_python×3 |
files: x.csv`. Old tool calls and tool outputs are not sent again: the full trace stays in the `messages`
column, the model only gets the gist. The `[this turn did]` line is written by turn_summary() from the turn's
own tool calls, no model involved. Variables are not in it, because the state block says what exists now.

The new question. build_context(question) starts the sandbox if needed, decides whether to add the restart
note (sandbox id now ≠ sandbox id of the last turn), and puts the state block on top of the question.

preview_context(question) prints exactly that, without calling the model.
"""
from collections import Counter

from pydantic_ai.messages import (ModelRequest, ModelResponse, UserPromptPart, TextPart,
                                  ToolCallPart, ToolReturnPart, CachePoint)

from . import current, sandbox_state
from .store import recent_turns, older_turns
from .sandbox_state import start_sandbox_if_needed, sandbox_restarted, state_block


def history_for_model():
    """The recent finished turns from SQLite, as question -> answer message pairs.
    Files a turn wrote that are no longer in /workspace are marked "(deleted since)"."""
    # a fixed first message ending in a cache breakpoint: system prompt + tools + this line are the same for
    # every question, so from the second question on they are read from the cache instead of sent again
    history = [ModelRequest(parts=[UserPromptPart(content=["Conversation so far:", CachePoint()])])]

    # turns older than the last KEEP_TURNS: one line each, the model can fetch_turn any of them
    if older_turns():
        lines = ["Earlier turns, one line each (fetch_turn gives the full question and answer):"]
        for t in older_turns():
            line = f"turn {t['turn']}: {t['model_summary']}"
            if " | files: " in t["summary"]:                # the files it wrote, from the [this turn did] line
                line += " | files: " + t["summary"].split(" | files: ")[1]
            lines.append(line)
        history.append(ModelRequest(parts=[UserPromptPart(content="\n".join(lines))]))

    for t in recent_turns():
        summary = t["summary"]                              # "tools: run_python×2 | files: a.csv, b.png"
        if " | files: " in summary:
            tools_part, files_part = summary.split(" | files: ")
            files = []
            for name in files_part.split(", "):
                if (current.WORKSPACE / name).exists():     # the sandbox's /workspace is this folder on the host
                    files.append(name)
                else:
                    files.append(f"{name} (deleted since)")
            summary = tools_part + " | files: " + ", ".join(files)
        history.append(ModelRequest(parts=[UserPromptPart(content=f"[turn {t['turn']}] {t['question']}")]))
        history.append(ModelResponse(parts=[TextPart(content=f"{t['answer']}\n\n[this turn did] {summary}")]))
    return history


def build_context(question):
    """(history, prompt, restart_note) for the next question."""
    start_sandbox_if_needed()
    restart_note = None
    if sandbox_restarted():
        restart_note = (f"restarted ({sandbox_state.LAST_STOP_REASON}); every earlier variable is gone, "
                        "files in /workspace are kept")
    history = history_for_model()
    prompt = state_block(restart_note) + "\n\n### question\n" + question
    return history, prompt, restart_note


def preview_context(question="(next question)"):
    """Print what the model would receive for this question (system prompt left out). Calls no model."""
    history, prompt, _ = build_context(question)
    for message in history:
        for part in message.parts:
            who = "USER " if isinstance(message, ModelRequest) else "MODEL"
            print(f"--- {who}: {part.content}\n")
    print(f"--- USER (new):\n{prompt}")


def tool_text(part):
    """The text of a tool result. With images the content is a list: text items and BinaryImage items;
    only the text is joined, the images are skipped."""
    if isinstance(part.content, str):
        return part.content
    texts = []
    for item in part.content:
        if isinstance(item, str):
            texts.append(item)
    return "\n".join(texts)


def names_after(text, prefix):
    """Names listed on the lines of a run_python result that start with prefix, e.g. 'figures saved: '.
    Only names that exist in /workspace count: the model's own print() output is in the same text and
    may contain a line like 'figures saved: none'."""
    names = []
    for line in text.splitlines():
        if line.startswith(prefix):
            for name in line[len(prefix):].split(", "):
                if (current.WORKSPACE / name).exists():
                    names.append(name)
    return names


def turn_summary(messages):
    """The [this turn did] line: which tools ran how often, which files were written."""
    tool_counts = Counter()
    files = []
    for message in messages:
        for part in message.parts:
            if isinstance(part, ToolCallPart) and part.tool_name != "final_result":
                tool_counts[part.tool_name] += 1
            if isinstance(part, ToolReturnPart) and part.tool_name == "run_python":
                files += names_after(tool_text(part), "figures saved: ")
                files += names_after(tool_text(part), "files written: ")
    tools_text = ", ".join(f"{name}×{n}" for name, n in tool_counts.items())
    summary = "tools: " + (tools_text or "none")
    if files:
        unique_files = list(dict.fromkeys(files))          # drop repeats, keep order
        summary += " | files: " + ", ".join(unique_files)
    return summary
