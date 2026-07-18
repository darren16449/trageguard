"""
Module 4: Vendor / Model Provenance Tracker

A register of every AI vendor and model touching the trading stack,
with a simple risk-scoring model and a mapping to the regulatory
frameworks most likely to apply (FINRA, SEC, EU AI Act, Treasury FS AI RMF).
"""
import pandas as pd
import streamlit as st

import db
from data.regulatory_mapping import FRAMEWORKS, suggest_frameworks, risk_tier_from_score

FRAMEWORK_BY_ID = {f["id"]: f for f in FRAMEWORKS}


def _compute_risk_score(training_disclosed, data_retention, audit_rights, region) -> int:
    score = 0
    if "not disclosed" in training_disclosed.lower() or "unknown" in training_disclosed.lower():
        score += 35
    elif "documented" not in training_disclosed.lower() and "internal" not in training_disclosed.lower():
        score += 15

    if "unknown" in data_retention.lower():
        score += 25
    elif "not used for training" not in data_retention.lower() and "n/a" not in data_retention.lower():
        score += 10

    if audit_rights.strip().lower().startswith("no"):
        score += 25
    elif "unclear" in audit_rights.lower():
        score += 15

    if "unknown" in region.lower():
        score += 15

    return min(100, score)


def render():
    st.header("Vendor & Model Provenance Tracker")
    st.caption(
        "62% of orgs can't say where all their LLMs are running. This register tracks every AI "
        "vendor/model in the trading stack, scores third-party risk, and maps each one to the "
        "regulatory frameworks most likely to apply."
    )

    vendors = db.fetch_vendors()
    df = pd.DataFrame(vendors)

    if len(df):
        c1, c2, c3 = st.columns(3)
        c1.metric("Vendors tracked", len(df))
        c2.metric("High/Critical risk", int(df["risk_tier"].isin(["High", "Critical"]).sum()))
        c3.metric("No audit rights", int(df["audit_rights_in_contract"].str.lower().str.startswith("no").sum()))

        st.subheader("Vendor register")

        def _color(v):
            return {
                "Low": "background-color: #d4edda", "Medium": "background-color: #fff3cd",
                "High": "background-color: #f8d7da", "Critical": "background-color: #f5c6cb",
            }.get(v, "")

        display_cols = ["name", "model_name", "purpose", "risk_score", "risk_tier",
                         "audit_rights_in_contract", "region"]
        st.dataframe(
            df[display_cols].rename(columns={
                "name": "Vendor", "model_name": "Model", "purpose": "Purpose",
                "risk_score": "Risk score", "risk_tier": "Risk tier",
                "audit_rights_in_contract": "Audit rights", "region": "Region",
            }).style.applymap(_color, subset=["Risk tier"]),
            use_container_width=True, hide_index=True,
        )

        st.subheader("Regulatory exposure for a vendor")
        vendor_names = df["name"].tolist()
        pick = st.selectbox("Select a vendor", vendor_names)
        row = df[df["name"] == pick].iloc[0]

        st.write(f"**Notes:** {row['notes']}")
        applicable = suggest_frameworks(row["purpose"], row.get("model_name", ""), row["region"])
        for fid in applicable:
            fw = FRAMEWORK_BY_ID.get(fid)
            if not fw:
                continue
            with st.expander(f"📋 {fw['name']}"):
                st.write(fw["summary"])
                st.caption(f"Applies when: {fw['applies_when']}")
    else:
        st.info("No vendors registered yet.")

    st.divider()
    st.subheader("Register a new vendor / model")
    with st.form("add-vendor"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Vendor name")
        model_name = c2.text_input("Model name / version")
        purpose = st.text_input("Purpose (what it's used for in the trading stack)")
        c3, c4 = st.columns(2)
        training_disclosed = c3.selectbox(
            "Training data disclosure",
            ["Documented (usage policy published)", "Fully documented (internal)",
             "Not disclosed", "Unknown"],
        )
        data_retention = c4.selectbox(
            "Data retention / training use",
            ["Not used for training per API terms", "N/A - internal", "Unknown"],
        )
        c5, c6 = st.columns(2)
        audit_rights = c5.selectbox(
            "Audit rights in contract", ["Yes - enterprise agreement", "Unclear - standard ToS only", "No"]
        )
        region = c6.text_input("Region", value="Unknown")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add vendor", type="primary")

    if submitted:
        if not name:
            st.warning("Vendor name is required.")
        else:
            score = _compute_risk_score(training_disclosed, data_retention, audit_rights, region)
            tier = risk_tier_from_score(score)
            db.insert_vendor(name, model_name, purpose, training_disclosed, data_retention,
                              audit_rights, region, score, tier, notes)
            st.success(f"Added {name} — risk score {score} ({tier}). Refresh below to see it in the register.")
            st.rerun()
