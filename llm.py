"""
TradeGuard - LLM wrapper.

Uses the real Anthropic API when an API key is available (via the
ANTHROPIC_API_KEY environment variable or entered in the Streamlit
sidebar). Falls back to a deterministic MOCK mode with no key so the
app is still fully explorable without one -- every module clearly
labels which mode produced a given response.
"""
import os
import random

_client = None
_api_key = None


def configure(api_key: str | None):
    """Set/refresh the API key used for LLM calls this session."""
    global _client, _api_key
    _api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    _client = None  # force re-init on next call


def is_live() -> bool:
    return bool(_api_key)


def _get_client():
    global _client
    if _client is None and _api_key:
        import anthropic
        _client = anthropic.Anthropic(api_key=_api_key)
    return _client


DEFAULT_MODEL = "claude-3-5-haiku-20241022"


def call(system_prompt: str, user_prompt: str, model: str = DEFAULT_MODEL,
          max_tokens: int = 400, temperature: float = 0.4) -> tuple[str, bool]:
    """
    Returns (text, was_live). was_live=False means the mock fallback
    was used (no API key configured, or a call failed).
    """
    client = _get_client()
    if client is None:
        return _mock_response(system_prompt, user_prompt), False

    try:
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        return text.strip(), True
    except Exception as e:
        return f"[LLM call failed, showing mock fallback] Error: {e}\n\n{_mock_response(system_prompt, user_prompt)}", False


def _mock_response(system_prompt: str, user_prompt: str) -> str:
    """Deterministic-ish canned response so the demo still functions offline."""
    rng = random.Random(hash(user_prompt) % (2**32))
    templates = [
        "Based on the observed inputs, this looks like a routine, explainable outcome consistent "
        "with the system's documented decision logic. (MOCK MODE - connect an API key for a live response.)",
        "The pattern in the data is ambiguous; a human reviewer should confirm before acting. "
        "(MOCK MODE - connect an API key for a live response.)",
        "This output cannot be fully justified from the visible inputs alone and should be flagged "
        "for audit. (MOCK MODE - connect an API key for a live response.)",
    ]
    return rng.choice(templates)
