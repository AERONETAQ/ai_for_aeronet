"""The terminal: a prompt loop. A line starting with / is a command, anything else is a question for the agent.

One agent for the whole session (built at start, so the Bedrock bearer token it carries lasts 12 hours);
the tools read the current conversation when they run. Nothing here calls the model except ask().
Every terminal is its own process: open another terminal, run the same command, /new or /load another
conversation; the container limit in the config is counted across all of them.
"""
import readline  # noqa: F401  (arrow keys and input history in input())
import signal

import sandbox as sb

from .. import config
from ..conversation import current, manage, sandbox_state
from ..conversation.store import all_turns
from ..conversation.sandbox_state import start_sandbox_if_needed, sandbox_id, sandbox_restarted, state_block
from ..conversation.context import preview_context
from ..agent.build import make_agent
from ..agent.prices import rates_line, start_price_updates
from ..agent.run import ask
from ..agent.tokens import calls_table, check_tokens
from . import view

HELP = """
/new <name>      create a conversation (folder + sandbox) and switch to it
/load <name>     switch to an existing conversation: starts its sandbox, shows its last turns
/list            every conversation: turns, cost, sandbox running or not
/delete <name>   stop its sandbox, delete its folder and its stored turns (asks first)
/history [n]     the last n turns of this conversation (default: keep_turns)
/turns           one row per turn: model calls, tokens, cost
/tokens <turn>   the model calls of one turn and the check against the stored row
/preview         what the model would receive for the next question (no model call)
/state           the sandbox state block
/stop            stop this conversation's sandbox (frees a slot; variables are lost, files stay)
/verbose         show the print flags; /verbose <flag> toggles one, /verbose all | none sets them all
/help            this list
/quit            leave, also plain quit or exit (sandboxes keep running until idle_minutes, or /stop them first)
anything else    a question for the agent
"""

NEEDS_CONVERSATION = {"history", "turns", "tokens", "preview", "state", "stop"}


def _interrupt(signum, frame):
    raise KeyboardInterrupt


# asyncio.run would install its own Ctrl-C handler, which swallows the first Ctrl-C at the prompt;
# with this one Ctrl-C raises KeyboardInterrupt wherever the terminal is: at the prompt or inside a question
signal.signal(signal.SIGINT, _interrupt)


def ensure_sandbox(say_running=False):
    """Make sure this conversation's sandbox is up, and say what happened: first start, left running (said only
    on /load), or restarted after an idle stop / crash / /stop (then the variables of the earlier turns are gone)."""
    if sb.running(current.ID):
        if say_running:
            view.console.print(f"[dim]sandbox {current.ID} is running (id {sandbox_id()}): left running from an "
                               "earlier session or open in another terminal; its variables are still there[/]")
        return
    with view.console.status(f"setting up sandbox {current.ID} ..."):
        start_sandbox_if_needed()                     # refuses when max_running_containers are already up
        env = sb.env(current.ID)
    view.console.print(f"sandbox {current.ID} started (id {sandbox_id()}): {env['memory_limit_mb']} MB RAM, "
                       f"{env['cpus']} CPUs, {env['workspace_cap_gb']} GB in /workspace, no network, stops after "
                       f"{config.SANDBOX['idle_minutes']} idle minutes; files in {current.WORKSPACE}")
    if sandbox_restarted():
        view.console.print(f"[yellow]the sandbox of the last turn is gone ({sandbox_state.LAST_STOP_REASON}): its "
                           "variables are lost, the files are kept; the model is told so with the next question[/]")


async def main():
    show = dict(config.VERBOSE)                        # the print flags; /verbose changes them for this session
    agent = make_agent()
    start_price_updates(agent.model.system)            # latest price table now and every hour (model.update_prices)
    view.console.print(f"[bold]AERONET agent[/] · {config.MODEL_ID} ({config.PROVIDER}) · reasoning "
                       f"{config.REASONING_EFFORT} · keep_turns {config.KEEP_TURNS} · config {config.CONFIG_FILE}")
    view.console.print(rates_line(agent.model.system))
    view.console.print("/new <name> or /load <name> to begin, /list shows the conversations, /help every command")

    while True:
        try:
            line = input(f"{current.ID or 'no conversation'}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break
        if not line:
            continue
        if line.lower() in ("quit", "exit", "q", "/quit", "/exit", "/q"):
            break

        # a question
        if not line.startswith("/"):
            if current.ID is None:
                view.console.print("no conversation loaded: /new <name> or /load <name>")
                continue
            try:
                ensure_sandbox()
                with view.console.status("working ..."):
                    row = await ask(agent, line, show=show)
            except Exception as e:
                view.console.print(f"[red]error:[/] {view.escape(f'{type(e).__name__}: {e}')}")
                continue
            if row:
                view.show_turn(row, show)
                view.show_cost(show)
            continue

        # a command
        cmd, _, arg = line[1:].partition(" ")
        arg = arg.strip()
        if cmd in NEEDS_CONVERSATION and current.ID is None:
            view.console.print("no conversation loaded: /new <name> or /load <name>")
            continue
        try:
            if cmd == "new":
                manage.create(arg)
                view.console.print(f"created conversation {arg}: folder {current.WORKSPACE}")
                ensure_sandbox()
                view.console.print("ready: type your first question")
            elif cmd == "load":
                manage.load(arg)
                view.console.print(f"loaded conversation {arg}: {len(all_turns())} turn(s) stored")
                ensure_sandbox(say_running=True)
                view.show_history(config.KEEP_TURNS, show)
                view.show_cost(show)
            elif cmd == "list":
                view.show_list(manage.list_all())
            elif cmd == "delete":
                answer = input(f"delete '{arg}': stop its sandbox, remove its folder and stored turns? [y/N] ")
                if answer.lower() == "y":
                    manage.delete(arg)
                    view.console.print(f"deleted {arg}")
            elif cmd == "history":
                view.show_history(int(arg) if arg else config.KEEP_TURNS, show)
            elif cmd == "turns":
                view.show_turns_table()
            elif cmd == "tokens":
                print(calls_table(int(arg)))
                check_tokens(int(arg))
            elif cmd == "preview":
                ensure_sandbox()
                preview_context()
            elif cmd == "state":
                ensure_sandbox()
                print(state_block())
            elif cmd == "stop":
                sb.stop(current.ID)
                view.console.print(f"sandbox {current.ID} stopped: variables gone, files kept; "
                                   "the next question starts a fresh one")
            elif cmd == "verbose":
                if arg in ("all", "none"):
                    show = {name: arg == "all" for name in show}
                elif arg in show:
                    show[arg] = not show[arg]
                elif arg:
                    view.console.print(f"no flag '{arg}'; the flags are: {', '.join(show)}")
                view.show_flags(show)
            elif cmd == "help":
                print(HELP)
            else:
                view.console.print(f"unknown command /{cmd}; /help lists them")
        except Exception as e:
            view.console.print(f"[red]error:[/] {view.escape(f'{type(e).__name__}: {e}')}")
