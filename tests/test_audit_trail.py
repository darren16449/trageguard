import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import audit_trail


def test_simulate_price_path_length_and_positive():
    prices = audit_trail._simulate_price_path(days=30, seed=42)
    assert len(prices) == 30
    assert all(p > 0 for p in prices)


def test_simulate_price_path_deterministic_with_seed():
    a = audit_trail._simulate_price_path(days=20, seed=7)
    b = audit_trail._simulate_price_path(days=20, seed=7)
    assert a == b


def test_decide_returns_valid_decision_and_confidence():
    prices = audit_trail._simulate_price_path(days=30, seed=1)
    decision, confidence, inputs = audit_trail._decide(prices)
    assert decision in ("BUY", "SELL", "HOLD")
    assert 0 <= confidence <= 1
    assert "last_price" in inputs


def test_decide_short_series_returns_hold():
    decision, confidence, inputs = audit_trail._decide([100.0, 101.0, 99.0])
    assert decision == "HOLD"
    assert confidence == 0.5


def test_decide_strong_uptrend_favors_buy():
    prices = [100 + i * 2 for i in range(30)]
    decision, confidence, inputs = audit_trail._decide(prices)
    assert decision == "BUY"


def test_decide_strong_downtrend_favors_sell():
    prices = [200 - i * 2 for i in range(30)]
    decision, confidence, inputs = audit_trail._decide(prices)
    assert decision == "SELL"


def test_decide_flat_prices_favors_hold():
    prices = [100.0] * 30
    decision, confidence, inputs = audit_trail._decide(prices)
    assert decision == "HOLD"
