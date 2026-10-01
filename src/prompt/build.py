"""Section 6 · The system prompt = rules + conversation rules + data dictionary + sandbox environment + skills
+ preamble rule, in that order, exactly as notebook 09 joined them."""
import sandbox as sb

from ..conversation import current
from ..conversation.sandbox_state import start_sandbox_if_needed
from ..skills import SKILLS_TEXT
from .rules import RULES, CONVERSATION_RULES, PREAMBLE_RULE
from .data_dictionary import DATA_DICTIONARY


def environment_block():
    start_sandbox_if_needed()
    env = sb.env(current.ID)
    return ("### sandbox environment\n"
            f"python {env['python']}; packages: " + ", ".join(f"{k} {v}" for k, v in env["packages"].items()) + "\n"
            f"limits: {env['memory_limit_mb']} MB RAM, {env['cpus']} CPUs, {env['workspace_cap_gb']} GB in /workspace, no network\n"
            f"pre-loaded in the kernel:\n{env['preloaded']}\n")


_INSTRUCTIONS = None


def instructions():
    """The whole system prompt. Built on first use (the environment block asks a running sandbox), then the
    same text for the rest of the session, so every question reads it from the prompt cache."""
    global _INSTRUCTIONS
    if _INSTRUCTIONS is None:
        _INSTRUCTIONS = "\n".join([RULES.strip(), CONVERSATION_RULES.strip(), DATA_DICTIONARY.strip(),
                                   environment_block(), "### skills\n" + SKILLS_TEXT, PREAMBLE_RULE.strip()])
    return _INSTRUCTIONS
