"""Section 4 · fetch_turn: the earlier turns of this conversation, read from SQLite. No model, no sandbox."""
from ..conversation.store import all_turns, recent_turns


def fetch_turn(turns: list[int]) -> str:
    '''The full question and answer of earlier turns that appear only as one line each in the "Earlier turns"
    index. turns = one or more turn numbers from that index. Returns no variables: only the "sandbox state now"
    block says what exists in the kernel; anything an earlier turn kept may be gone.'''
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
