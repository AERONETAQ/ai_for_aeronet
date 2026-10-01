"""Section 7 · Answer shape, model, agent.

output_type=Turn makes the model end every question by calling a final_result tool with answer,
kept_variables and summary (the index line of this turn). Pydantic AI checks the JSON and asks again if it is
malformed (a retry, one more request). LIMITS bound one question; config conv_cost_limit bounds the conversation.

Output validator. files_exist runs on every final_result the model produces, inside the agent loop: each
/workspace/<file> the answer names must exist on disk, else ModelRetry sends the answer back (one more model
call, counted like any other; it shares retries).

Model settings (max_tokens, reasoning effort) apply to EVERY model call of the loop, one call at a time:
max_tokens is the output cap of one step, not of the question. The per-question caps are LIMITS.
"""
import re

from pydantic import BaseModel, Field
from aws_bedrock_token_generator import provide_token
from pydantic_ai import Agent, UsageLimits, ModelRetry
from pydantic_ai.models.bedrock_mantle import BedrockMantleResponsesModel, BedrockMantleProvider
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIResponsesModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

from .. import config
from ..conversation import current
from ..tools import TOOLS
from ..prompt.build import instructions
from .prices import apply_custom_prices


class KeptVar(BaseModel):
    name: str    = Field(description="exact variable name in the kernel")
    meaning: str = Field(description="one line: what it holds (site, period, wavelength, unit) and why a follow-up could reuse it")


class Turn(BaseModel):
    answer: str                  = Field(description="the complete markdown answer, exactly as you would write it to the user")
    kept_variables: list[KeptVar] = Field(description="every variable you left in the kernel on purpose; temporaries are deleted")
    summary: str                 = Field(description="one line, at most 20 words: what was asked and what came out (site, period, quantity, files written). It is this turn's line in the index of earlier turns")


LIMITS = UsageLimits(**config.LIMITS)


def make_model():
    """The model named in the config. This is the only place that knows the provider.
    bedrock-mantle: GPT-5.6 Luna on Bedrock Mantle (Responses API), bearer token minted now, lasts 12 hours.
    openai-compatible: any server speaking OpenAI chat completions at base_url (LM Studio, Ollama, vLLM).
    No reasoning effort, no prompt cache key, no cost (set limits.cost_limit to null); the model must support
    tool calling, since the tools and the final_result answer are tool calls."""
    if config.PROVIDER == "bedrock-mantle":
        return BedrockMantleResponsesModel(
            config.MODEL_ID,
            provider=BedrockMantleProvider(base_url=config.BASE_URL, api_key=provide_token(region=config.REGION)),
            settings=OpenAIResponsesModelSettings(max_tokens=config.MAX_TOKENS,
                                                  openai_reasoning_effort=config.REASONING_EFFORT,
                                                  openai_prompt_cache_key=config.PROMPT_CACHE_KEY),
        )
    if config.PROVIDER == "openai-compatible":
        return OpenAIChatModel(
            config.MODEL_ID,
            provider=OpenAIProvider(base_url=config.BASE_URL, api_key=config.API_KEY),
            settings=ModelSettings(max_tokens=config.MAX_TOKENS),
        )
    raise ValueError(f"model.provider must be bedrock-mantle or openai-compatible, not {config.PROVIDER!r}")


def files_exist(ctx, turn: Turn) -> Turn:
    """Every /workspace/<file> the answer names must be on disk; otherwise the model gets the answer back."""
    named = set(name.rstrip(".,;:") for name in re.findall(r"/workspace/([\w.\-]+)", turn.answer))
    missing = [name for name in named if not (current.WORKSPACE / name).exists()]
    if missing:
        raise ModelRetry(f"the answer names files that do not exist in /workspace: {', '.join(missing)}. "
                         "Create them, or remove the reference from the answer.")
    return turn


def make_agent(model=None):
    """The agent of notebook 09. One agent serves every conversation: the tools read the current conversation
    when they run. instructions is a function, read when the first question runs (it needs a sandbox for the
    environment block), so the agent can be built before any conversation is loaded. model: for tests."""
    model = model or make_model()
    apply_custom_prices(model.system)        # config model.prices over the built-in price table
    agent = Agent(model, instructions=instructions, tools=TOOLS, output_type=Turn,
                  retries=config.RETRIES, tool_timeout=config.TOOL_TIMEOUT)
    agent.output_validator(files_exist)
    return agent
