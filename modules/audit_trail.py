"""
Module 1: Explainability & Audit Trail

Simulates a momentum-based trading signal engine over synthetic price
data, generates BUY/SELL/HOLD decisions, and asks the LLM to produce a
plain-English rationale for each decision - the kind of artifact a
firm needs on hand when a regulator or compliance officer asks
"why did the algo do that?" (see Q9 in the source governance notes,
and SEC 2026 exam priorities on AI supervision).
"""
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

import db
import llm

TICKERS = ["ACME", "NORTH", "VALEO", "QTECH", "BRIX"]

EXPLAIN_SYSTEM_PROMPT = """You are an explainability assistant for a trading firm's compliance team.
Given a trading signal engine's raw inputs and its decision, write a SHORT (2-3 sentence), plain-English
explanation of why the engine likely made that decision, suitable for a compliance audit log. Be concrete
about which input(s) drove the decision. Do not use jargon a non-technical auditor wouldn't understand.
If the decision looks statistically weak or hard to justify from the inputs, say so plainly instead of
inventing a confident-sounding rationale."""


def _simulate_price_path(days=30, seed=None):
    rng = np.random.default_rng(seed)
    prices = [100.0]
    for _ in range(days - 1):
        prices.append(max(1.0, prices[-1] * (1 + rng.normal(0, 0.018))))
    return prices


def _decide(prices):
    """Simple momentum rule: compare short vs long moving average."""
    s = pd.Series(prices)
    short_ma = s.rolling(5).mean().iloc[-1]
    long_ma = s.rolling(15).mean().iloc[-1]
    momentum = (prices[-1] - prices[-6]) / prices[-6] if len(prices) > 6 else 0
    if pd.isna(short_ma) or pd.isna(long_ma):
        return "HOLD", 0.5, {"short_ma": None, "long_ma": None, "momentum_5d_pct": round(momentum * 100, 2)}

    spread = (short_ma - long_ma) / long_ma
    if spread > 0.01:
        decision, confidence = "BUY", min(0.95, 0.5 + spread * 10)
    elif spread < -0.01:
        decision, confidence = "SELL", min(0.95, 0.5 + abs(spread) * 10)
    else:
        decision, confidence = "HOLD", 0.5

    inputs = {
        "short_ma_5d": round(short_ma, 2),
        "long_ma_15d": round(long_ma, 2),
        "spread_pct": round(spread * 100, 2),
        "momentum_5d_pct": round(momentum * 100, 2),
        "last_price": round(prices[-1], 2),
    }
    return decision, round(confidence, 2), inputs


def run_trading_day(system_name="Momentum Signal Engine"):
    for ticker in TICKERS:
        seed = random.randint(0, 1_000_000)
        prices = _simulate_price_path(days=30, seed=seed)
        decision, confidence, inputs = _decide(prices)

        user_prompt = (
            f"Ticker: {ticker}\nDecision made by the engine: {decision}\n"
            f"Confidence: {confidence}\nRaw inputs: {inputs}\n\n"
            "Explain this decision for the audit log."
        )
        explanation, was_live = llm.call(EXPLAIN_SYSTEM_PROMPT, user_prompt, max_tokens=150)
        tag = "" if was_live else " *(mock mode)*"
        db.insert_audit_entry(system_name, ticker, decision, inputs, explanation + tag, confidence)


def render():
    st.header("Explainability & Audit Trail")
    st.caption(
        "Every trading decision should be reconstructable in plain English on demand. "
        "This module simulates a momentum signal engine and logs an LLM-generated rationale "
        "for each decision, the way a compliance team would need for an SEC/FINRA inquiry."
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("▶ Run a new trading cycle", type="primary"):
            with st.spinner("Generating signals and explanations..."):
                run_trading_day()
            st.success("Trading cycle logged.")

    entries = db.fetch_audit_log(limit=300)
    if not entries:
        st.info("No decisions logged yet - run a trading cycle above.")
        return

    df = pd.DataFrame(entries)
    df["ts"] = pd.to_datetime(df["ts"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Decisions logged", len(df))
    m2.metric("With explanation", int((df["explanation"].str.len() > 0).sum()))
    m3.metric("Avg confidence", f"{df['confidence'].mean():.0%}")
    m4.metric("Distinct tickers", df["ticker"].nunique())

    st.subheader("Decision log")
    decision_filter = st.multiselect("Filter by decision", ["BUY", "SELL", "HOLD"], default=["BUY", "SELL", "HOLD"])
    filtered = df[df["decision"].isin(decision_filter)]
    st.dataframe(
        filtered[["ts", "ticker", "decision", "confidence", "explanation"]].sort_values("ts", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Inspect a decision")
    if len(filtered):
        idx = st.selectbox(
            "Pick a row (most recent first)",
            filtered.sort_values("ts", ascending=False).index,
            format_func=lambda i: f"{filtered.loc[i, 'ts']} — {filtered.loc[i, 'ticker']} — {filtered.loc[i, 'decision']}",
        )
        row = filtered.loc[idx]
        st.json(row["inputs_json"])
        st.write(f"**Explanation:** {row['explanation']}")
