"""Section 8 · ask().

The five steps: budget, build the context, run (every step printed), store one row in SQLite, kernel cleanup.
A turn stopped by a limit is stored too (status='stopped', its tokens and cost counted) but never shown to the
model again. drop_images() removes the image items from the turn's messages before they go into SQLite: the
`[image: name, WxH px, ≈N tokens]` line before each one stays, the PNG itself is on disk in the workspace folder.

Differences from the notebook: ask() takes the agent as a parameter and returns the stored row (a dict with the
turn number) instead of printing the answer; the terminal renders it. What is printed while the loop runs is
chosen by `show`, the terminal.verbose flags of the config: tool_calls = everything, as the notebook printed it;
otherwise steps = one line per step (the model's preamble sentence) and step_tokens = its tokens and cost.
"""
import json
from datetime import datetime, timezone

from pydantic_ai import Agent, UsageLimitExceeded
from pydantic_ai.messages import (ModelMessagesTypeAdapter, UserPromptPart, TextPart, ThinkingPart, ToolCallPart,
                                  ToolReturnPart, RetryPromptPart)

from .. import config
from ..conversation.store import save_turn, token_columns, conversation_cost, recent_turns
from ..conversation.sandbox_state import sandbox_id, cleanup_kernel
from ..conversation.context import build_context, tool_text, turn_summary
from .build import LIMITS


def show_part(p, preamble=False):
    if isinstance(p, UserPromptPart):
        print(f"  >>> USER        : {p.content}")
    elif isinstance(p, ThinkingPart):
        print(f"  ... THINKING    : {p.content or '<no text>'}")
    elif isinstance(p, TextPart):
        print(f"  <<< {'PREAMBLE' if preamble else 'ANSWER  '}    : {p.content}")
    elif isinstance(p, ToolCallPart):
        print(f"  --> TOOL CALL   : {p.tool_name}({p.args})")
    elif isinstance(p, ToolReturnPart):
        print(f"  <-- TOOL RESULT : {p.tool_name} -> {tool_text(p)}")
    elif isinstance(p, RetryPromptPart):
        print(f"  !!! RETRY       : {p.tool_name}: {p.content}")


def usage_line(u):
    """Tokens and cost of one model call (RequestUsage) or of a whole turn (RunUsage)."""
    uncached  = u.input_tokens - u.cache_read_tokens - u.cache_write_tokens
    reasoning = u.details.get("reasoning_tokens", "n/a")
    cost      = f"${u.cost:.4f}" if u.cost is not None else "cost n/a"
    return (f"in {u.input_tokens} (uncached {uncached}, cache read {u.cache_read_tokens}, "
            f"cache write {u.cache_write_tokens}) | out {u.output_tokens} (reasoning {reasoning}) | {cost}")


def preamble_of(response):
    """The sentence the model wrote before its tool calls; "final answer" for the final_result call;
    the tool names when it wrote nothing."""
    text = " ".join(p.content for p in response.parts if isinstance(p, TextPart)).strip()
    tools = [p.tool_name for p in response.parts if isinstance(p, ToolCallPart)]
    if text:
        return text
    if tools == ["final_result"]:
        return "final answer"
    return "(no preamble) " + ", ".join(tools)


async def print_steps(run, show):
    """Walk the agent loop node by node. show["tool_calls"]: everything that goes to and comes from the model, as
    in the notebook. Otherwise show["steps"]: the model's preamble sentence per step; show["step_tokens"]: its
    tokens and cost."""
    step = 0
    so_far = 0     # cost of this question up to and including the current step
    async for node in run:
        if Agent.is_model_request_node(node):
            step += 1
            if show.get("tool_calls"):
                print(f"\n--- step {step}: to model")
                for p in node.request.parts:
                    show_part(p)
            elif show.get("steps"):
                for p in node.request.parts:
                    if isinstance(p, RetryPromptPart):
                        print(f"  retry -> {p.tool_name}: {p.content}")
        elif Agent.is_call_tools_node(node):
            response = node.model_response
            so_far += response.usage.cost or 0
            so_far_text = f" | so far ${so_far:.4f}"
            if show.get("tool_calls"):
                print(f"--- step {step}: from model")
                for p in response.parts:
                    show_part(p, preamble=bool(response.tool_calls))
                print(f"      {usage_line(response.usage)}{so_far_text}")
            else:
                if show.get("steps"):
                    print(f"step {step}: {preamble_of(response)}")
                if show.get("step_tokens"):
                    print(f"        {usage_line(response.usage)}{so_far_text}")


def drop_images(messages):
    """Remove every image from the turn's messages (the label line before each one stays). The files are on disk."""
    for message in messages:
        for part in message.parts:
            if isinstance(part, ToolReturnPart) and isinstance(part.content, list):
                part.content = [item for item in part.content if isinstance(item, str)]


async def ask(agent, question, limits=LIMITS, show=None):
    """One question. Returns the stored row as a dict (with "turn"), or None when the conversation budget is used up.
    show: the terminal.verbose flags (default: the config's)."""
    if show is None:
        show = config.VERBOSE
    # 1 · budget
    spent = conversation_cost()
    if config.CONV_COST_LIMIT is not None and spent >= config.CONV_COST_LIMIT:
        print(f"=== conversation budget used: ${spent:.4f} of ${config.CONV_COST_LIMIT}. Start a new conversation.")
        return None

    # 2 · build the context: history from SQLite + state block from the sandbox (section 3)
    history, prompt, restart_note = build_context(question)
    if show.get("tool_calls"):
        print(f"=== {question}\n    ({len(recent_turns())} earlier turns in context; conversation so far ${spent:.4f})")

    # 3 · run
    status = "ok"
    async with agent.iter(prompt, message_history=history, usage_limits=limits) as run:
        try:
            await print_steps(run, show)
        except UsageLimitExceeded as e:
            status = "stopped"
            print(f"\n=== STOPPED: {e}\n    (cost counted; the model will not see this turn)")

    # 4 · store
    messages = run.new_messages()
    drop_images(messages)                    # image bytes are not stored; the PNGs are in the workspace folder
    row = {
        "asked":        datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status":       status,
        "question":     question,
        "answer":       None,
        "summary":      turn_summary(messages),
        "model_summary": None,
        "variables":    None,
        "sandbox":      sandbox_id(),        # read now: run_python may have restarted it during the turn
        "restart_note": restart_note,
        "requests":     run.usage.requests,
        "tool_calls":   run.usage.tool_calls,
        **token_columns(run.usage),
        "messages":     ModelMessagesTypeAdapter.dump_json(messages).decode(),
    }
    if status == "ok":
        out = run.result.output
        row["answer"] = out.answer
        row["model_summary"] = out.summary
        row["variables"] = json.dumps([v.model_dump() for v in out.kept_variables])
    row["turn"] = save_turn(row)

    # 5 · kernel cleanup (only after a finished turn)
    if status == "ok":
        kept, deleted = cleanup_kernel()
        if show.get("tool_calls"):
            print(f"\n=== KERNEL: kept {', '.join(kept) or 'nothing'} | deleted {', '.join(deleted) or 'nothing'}")
    return row
