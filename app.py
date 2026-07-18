"""
TradeGuard - AI Governance Platform for Trading & Investment Systems

A working demo platform covering four governance functions for AI used
on a trading desk:
  1. Explainability & audit trail for trading decisions
  2. Red-team-as-a-service prompt-injection testing for AI copilots
  3. Incident response tabletop simulator
  4. Vendor / model provenance tracker with regulatory mapping

Run with:  streamlit run app.py
"""
import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

import db
import llm
from modules import audit_trail, redteam, incident_sim, vendor_tracker

st.set_page_config(page_title="TradeGuard - AI Governance for Trading", page_icon="🛡️", layout="wide")

db.init_db()

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("🛡️ TradeGuard")
    st.caption("AI Governance Platform for Trading & Investment Systems")

    api_key_input = st.text_input(
        "Anthropic API key (optional)",
        type="password",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        help="Paste an Anthropic API key to get live LLM responses in the Audit Trail, "
             "Red-Team, and Incident Simulator modules. Without a key, those modules run "
             "in a clearly-labeled mock mode so you can still explore the whole app.",
    )
    llm.configure(api_key_input)
    if llm.is_live():
        st.success("Live LLM mode (Anthropic API connected)")
    else:
        st.warning("Mock mode — no API key set")

    st.divider()
    page = st.radio(
        "Module",
        ["Overview", "Explainability & Audit Trail", "Red-Team: Copilot Attacks",
         "Incident Response Simulator", "Vendor & Model Tracker"],
    )
    st.divider()
    st.caption(
        "Built on a 10-question AI governance framework and research into FINRA/SEC guidance, "
        "the EU AI Act, the Treasury Financial Services AI RMF, and real incidents "
        "(Knight Capital, deepfake-driven market moves, prompt-injection leaks). "
        "See README.md for sources. Educational demo — not legal advice."
    )

# ---------------------------------------------------------------- pages
if page == "Overview":
    st.header("TradeGuard: AI Governance for Trading & Investment Systems")
    st.markdown(
        "AI is now embedded across the trading lifecycle — signal generation, execution, "
        "robo-advice, and research copilots. Each of those carries a different governance "
        "failure mode. This platform gives you a working demo of four controls a trading "
        "firm needs in place, grounded in real regulation and real incidents."
    )

    systems = db.fetch_ai_systems()
    if systems:
        st.subheader("AI systems inventory (seeded example)")
        df = pd.DataFrame(systems)
        st.dataframe(
            df[["name", "system_type", "description", "autonomy_level", "risk_classification"]].rename(
                columns={"name": "System", "system_type": "Type", "description": "Description",
                         "autonomy_level": "Autonomy", "risk_classification": "Risk"}
            ),
            use_container_width=True, hide_index=True,
        )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("#### 1. Explainability")
        st.caption("Can you explain any trading decision in plain English, on demand?")
    with c2:
        st.markdown("#### 2. Red-Team")
        st.caption("Does your AI copilot resist prompt injection and unauthorized actions?")
    with c3:
        st.markdown("#### 3. Incident Response")
        st.caption("Is your team drilled on AI-specific incident scenarios?")
    with c4:
        st.markdown("#### 4. Vendor Risk")
        st.caption("Do you know every AI vendor/model in your stack, and its regulatory exposure?")

    st.divider()
    st.subheader("Why this matters (research grounding)")
    st.markdown(
        "- **Knight Capital (2012):** a dormant algorithm flag was reactivated during a deployment "
        "and lost $440M in 45 minutes — the canonical case for kill-switches and deployment review.\n"
        "- **FINRA's 2026 Annual Regulatory Oversight Report** found a 5x jump in member-reported "
        "AI use cases (3 in 2025 → 15 in 2026), and flags supervision, recordkeeping, and fair-dealing "
        "rules as already applicable to GenAI.\n"
        "- **The SEC's 2026 exam priorities** focus on whether firms have adequate policies to "
        "supervise AI use, after withdrawing its 2023 predictive data analytics rule proposal.\n"
        "- **The EU AI Act** classifies AI systems evaluating creditworthiness as high-risk (Annex III(5)(b)), "
        "and robo-advisors may qualify depending on their decision-making autonomy — full obligations "
        "apply to new high-risk systems deployed from August 2026.\n"
        "- **Deepfake-driven market moves** are a live and growing risk: a fabricated 2023 image "
        "briefly moved Dow futures, and deepfake videos of real executives have been used to push "
        "fake stock recommendations.\n"
        "- **The U.S. Treasury's Financial Services AI Risk Management Framework** (Feb 2026, with the "
        "Cyber Risk Institute) adapts NIST's Govern/Map/Measure/Manage structure specifically for "
        "financial institutions, including third-party/vendor risk."
    )

elif page == "Explainability & Audit Trail":
    audit_trail.render()

elif page == "Red-Team: Copilot Attacks":
    redteam.render()

elif page == "Incident Response Simulator":
    incident_sim.render()

elif page == "Vendor & Model Tracker":
    vendor_tracker.render()
