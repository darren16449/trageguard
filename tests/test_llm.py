import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import llm


def test_mock_mode_when_no_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    llm.configure(None)
    assert llm.is_live() is False
    text, was_live = llm.call("system prompt", "user prompt")
    assert was_live is False
    assert isinstance(text, str) and len(text) > 0


def test_configure_with_key_reports_live(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    llm.configure("fake-key-for-testing")
    assert llm.is_live() is True
    # reset so this test doesn't leak state into other tests
    llm.configure(None)
