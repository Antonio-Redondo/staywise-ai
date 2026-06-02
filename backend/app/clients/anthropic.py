import os
from typing import Any, Dict, List

try:
    from anthropic import Anthropic
except Exception:  # pragma: no cover - runtime import ok
    Anthropic = None


API_KEY = os.getenv("ANTHROPIC_API_KEY")


def _make_client():
    if Anthropic is None:
        return None
    return Anthropic(api_key=API_KEY)


# Module-level singletons
claude_sonnet = _make_client()
claude_opus = claude_sonnet  # alias; use different model names when calling


def call_structured(model, prompt: List[Dict[str, Any]], schema=None):
    """Placeholder helper to call an Anthropic client with structured output.
    Real implementation should use the project's structured-output helper or
    withStructuredOutput equivalent for the Anthropic/LLM wrapper used.
    """
    client = claude_sonnet if model == "sonnet" else claude_opus
    if client is None:
        raise RuntimeError("Anthropic client not configured")
    # The exact API varies; callers should build wrapper functions per project conventions
    return client
