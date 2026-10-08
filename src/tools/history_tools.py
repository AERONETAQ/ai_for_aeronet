"""Section 4 · fetch_turn: the earlier turns of this conversation, read from SQLite. No model, no sandbox."""
from ..conversation.store import all_turns, recent_turns


def fetch_turn(turns: list[int]) -> str:
    '''The full question and answer of earlier turns that appear only as one line each in the "Earlier turns"
    index. turns = one or more turn numbers from that index. Returns no variables: only the "sandbox state now"
    block says what exists in the kernel; anything an earlier turn kept may be gone.
    Limits: the question, answer and summary text of this conversation's finished turns only: no tool outputs,
    no code, no figures (view_figure) and no files (read them in run_python); a turn that is already in your
    context is not repeated; numbers in an old answer are that turn's, recompute when the question needs them.

    Args:
        turns: the turn numbers to fetch, as the "Earlier turns" index shows them, e.g. [3] or [2, 5].
    '''
    shown = [t["turn"] for t in recent_turns()]             # already in the context in full
    parts = []
    for n in turns:
        row = None
        for t in all_turns():
            if t["turn"] == n and t["status"] == "ok":
                row = t
        if row is None:
            parts.append(f"turn {n}: no such turn")
        elif n in shown:
            parts.append(f"turn {n}: already in your context in full")
        else:
            parts.append(f"### turn {n}\nquestion: {row['question']}\n\nanswer:\n{row['answer']}\n\n"
                         f"[this turn did] {row['summary']}")
    return "\n\n".join(parts)
