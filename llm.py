"""Optional LLM-based answer synthesis (Step 2 + Step 3 of the build process).

Configured to use OpenAI exclusively.
"""
import os
from typing import List, Tuple

from .chunking import Passage
from .prompts import SYSTEM_PROMPT

# Default OpenAI model. Override with RESEARCH_AGENT_MODEL_OPENAI if desired.
OPENAI_MODEL = os.environ.get("RESEARCH_AGENT_MODEL_OPENAI", "gpt-4o-mini")

# Backwards-compatible override: if RESEARCH_AGENT_MODEL is set, it takes precedence.
_LEGACY_MODEL_OVERRIDE = os.environ.get("RESEARCH_AGENT_MODEL")


def get_active_provider() -> str:
    """Always targets OpenAI since we are running in single-provider mode."""
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return ""  # No key configured


def get_active_model() -> str:
    if _LEGACY_MODEL_OVERRIDE:
        return _LEGACY_MODEL_OVERRIDE
    return OPENAI_MODEL


# Kept for backwards compatibility with test_connection.py
MODEL_NAME = get_active_model()


def _build_user_message(question: str, ranked_passages: List[Tuple[Passage, float]]) -> str:
    numbered = "\n\n".join(
        f"[S{i + 1}] (source: {p.source}) {p.text}"
        for i, (p, _score) in enumerate(ranked_passages)
    )
    return f"Question: {question}\n\nSource passages:\n\n{numbered}"


def _synthesize_with_openai(question: str, ranked_passages: List[Tuple[Passage, float]]) -> str:
    import openai  # imported lazily so the rest of the agent works without it

    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=get_active_model(),
        max_tokens=600,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_message(question, ranked_passages)},
        ],
    )
    return response.choices[0].message.content


def synthesize_with_llm(question: str, ranked_passages: List[Tuple[Passage, float]]) -> str:
    """Call OpenAI to synthesize a cited answer."""
    provider = get_active_provider()
    if provider == "openai":
        return _synthesize_with_openai(question, ranked_passages)
    raise RuntimeError(
        "No OpenAI API key configured. Set OPENAI_API_KEY in your environment or .env file."
    )