"""What the terminal prints. Text only: a figure is a path the user opens themselves."""
import json
import re

from rich.console import Console
from rich.markdown import Markdown
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from .. import config
from ..conversation import current
from ..conversation.store import all_turns, conversation_cost, show_turns

console = Console()


def render(text):
    """The answer as the model wrote it, with every file it names as a path on this machine the user can open:
    a markdown link [label](sandbox:/workspace/x.png) becomes "label (<folder>/x.png)", a bare /workspace/x.csv
    becomes <folder>/x.csv."""
    text = re.sub(r"\[([^\]]*)\]\((?:sandbox:)?/workspace/([^)\s]+)\)", r"\1 (/workspace/\2)", text)
    folder = str(current.WORKSPACE)
    return text.replace("sandbox:/workspace/", folder + "/").replace("/workspace/", folder + "/")


def files_of(row):
    """Files the turn wrote, from its [this turn did] line, as paths on this machine."""
    if " | files: " not in row["summary"]:
        return []
    return [current.WORKSPACE / name for name in row["summary"].split(" | files: ")[1].split(", ")]


def tokens_line(row):
    """Same shape as run.usage_line, from a stored row."""
    reasoning = row["reasoning_tokens"] if row["reasoning_tokens"] is not None else "n/a"
    cost = f"${row['cost_usd']:.4f}" if row["cost_usd"] is not None else "cost n/a"
    return (f"in {row['input_tokens']} (uncached {row['uncached_input']}, cache read {row['cache_read']}, "
            f"cache write {row['cache_write']}) | out {row['output_tokens']} (reasoning {reasoning}) | {cost}")


def show_turn(row, show):
    """One stored turn: the question and the answer always; summary, kept variables, files and the turn's tokens
    when the matching terminal.verbose flag (show) is on."""
    console.rule(f"turn {row['turn']}")
    console.print(f"[bold cyan]Q:[/] {escape(row['question'])}")
    if row["status"] != "ok":
        console.print("[red]stopped by a usage limit: no answer stored[/]")
    else:
        console.print(Panel(Markdown(render(row["answer"])), title="answer", border_style="green"))
        if show.get("summary"):
            console.print(f"[dim]summary: {escape(row['model_summary'] or '')}[/]")
        variables = json.loads(row["variables"] or "[]")
        if show.get("kept_variables") and variables:
            console.print("[dim]kept variables: " + escape(", ".join(f"{v['name']} ({v['meaning']})" for v in variables)) + "[/]")
    if show.get("files"):
        for path in files_of(row):
            console.print(f"[dim]file: {path}{'' if path.exists() else ' (deleted since)'}[/]")
    if show.get("turn_tokens"):
        console.print(f"[dim]{row['requests']} model calls, {row['tool_calls']} tool calls | {escape(tokens_line(row))}[/]")


def show_cost(show):
    if not show.get("conversation_cost"):
        return
    limit = f" of ${config.CONV_COST_LIMIT}" if config.CONV_COST_LIMIT is not None else ""
    console.print(f"[bold]conversation {current.ID}: ${conversation_cost():.4f}{limit}[/]")


def show_history(n, show):
    """The last n stored turns."""
    turns = all_turns()
    if not turns:
        console.print("no turns yet")
        return
    console.print(f"[dim]{len(turns)} turn(s); showing the last {min(n, len(turns))}[/]")
    for row in turns[-n:]:
        show_turn(row, show)


def show_flags(show):
    """The terminal.verbose flags as they are now."""
    console.print("  ".join(f"{name} [{'green' if on else 'red'}]{'on' if on else 'off'}[/]" for name, on in show.items()))


def show_list(rows):
    """Every conversation: turns, cost, last question, sandbox running or not."""
    table = Table("conversation", "turns", "cost", "last question (UTC)", "sandbox")
    for r in rows:
        table.add_row(r["name"], str(r["turns"]), f"${r['cost']:.4f}", r["last"][:19].replace("T", " "),
                      "[green]running[/]" if r["running"] else "-")
    console.print(table)


def show_turns_table():
    """One row per turn: model calls, tool calls, tokens and cost (store.show_turns() has every column)."""
    table = Table("turn", "time (UTC)", "status", "question", "calls", "tools", "in", "cache read", "out", "reasoning", "cost")
    for _, r in show_turns().iterrows():
        cost = f"{r['cost_usd']:.4f}" if isinstance(r["cost_usd"], float) and r["cost_usd"] == r["cost_usd"] else "-"   # None/NaN = not reported
        table.add_row(str(r["turn"]), str(r["asked"])[11:19], r["status"], str(r["question"])[:40],
                      str(r["requests"]), str(r["tool_calls"]), str(r["input_tokens"]), str(r["cache_read"]),
                      str(r["output_tokens"]), str(r["reasoning_tokens"]), cost)
    console.print(table)
