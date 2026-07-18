"""
Module 3: AI Incident Response Simulator

Finance-specific tabletop scenarios (grounded in real precedents like
Knight Capital and deepfake-driven market moves), scored against a
best-practice checklist, with an optional LLM-generated after-action
report.
"""
import streamlit as st

import db
import llm
from data.incident_scenarios import SCENARIOS

AAR_SYSTEM_PROMPT = """You are an AI incident-response coach for a trading firm. Given a tabletop
scenario, the questions asked, the answers the team chose, and which answers were best-practice,
write a SHORT after-action report (4-6 sentences): what the team got right, the single biggest gap,
and one concrete action item for next week. Be direct and specific, not generic."""


def render():
    st.header("AI Incident Response Simulator")
    st.caption(
        "46% of firms have no AI-specific incident response plan. These tabletop drills are "
        "modeled on real trading-AI incidents so your team can rehearse the first 15 minutes "
        "before it happens for real."
    )

    scenario_names = {s["id"]: s["name"] for s in SCENARIOS}
    chosen_id = st.selectbox(
        "Choose a scenario", list(scenario_names.keys()), format_func=lambda i: scenario_names[i]
    )
    scenario = next(s for s in SCENARIOS if s["id"] == chosen_id)

    st.info(f"**Precedent:** {scenario['source_note']}")
    st.markdown(f"### Scenario\n{scenario['narrative']}")

    st.markdown("### Your response")
    answers = []
    with st.form(key=f"form-{chosen_id}"):
        for i, q in enumerate(scenario["questions"]):
            choice = st.radio(q["q"], q["options"], index=None, key=f"{chosen_id}-{i}")
            answers.append(choice)
        submitted = st.form_submit_button("Score my response", type="primary")

    if submitted:
        if any(a is None for a in answers):
            st.warning("Answer every question before scoring.")
            return

        score = 0
        breakdown = []
        for q, a in zip(scenario["questions"], answers):
            chosen_idx = q["options"].index(a)
            correct = chosen_idx == q["best"]
            score += 1 if correct else 0
            breakdown.append({
                "question": q["q"], "your_answer": a,
                "best_practice": q["options"][q["best"]], "correct": correct,
            })

        max_score = len(scenario["questions"])
        pct = score / max_score

        if pct == 1.0:
            st.success(f"Score: {score}/{max_score} — strong readiness.")
        elif pct >= 0.5:
            st.warning(f"Score: {score}/{max_score} — partial readiness, gaps to close.")
        else:
            st.error(f"Score: {score}/{max_score} — significant gaps.")

        st.progress(pct)

        for b in breakdown:
            icon = "✅" if b["correct"] else "❌"
            with st.expander(f"{icon} {b['question']}"):
                st.write(f"**Your answer:** {b['your_answer']}")
                if not b["correct"]:
                    st.write(f"**Best practice:** {b['best_practice']}")

        with st.spinner("Generating after-action report..."):
            aar_input = (
                f"Scenario: {scenario['name']}\n{scenario['narrative']}\n\n"
                f"Results: {score}/{max_score} correct.\n"
                + "\n".join(
                    f"- Q: {b['question']}\n  Chosen: {b['your_answer']}\n  Best practice: {b['best_practice']}\n  Correct: {b['correct']}"
                    for b in breakdown
                )
            )
            aar, was_live = llm.call(AAR_SYSTEM_PROMPT, aar_input, max_tokens=250)
            if not was_live:
                aar += " *(mock mode)*"

        st.subheader("After-action report")
        st.write(aar)

        db.insert_incident_run(chosen_id, scenario["name"], score, max_score, answers, aar)

    st.subheader("Past drills")
    runs = db.fetch_incident_runs()
    if runs:
        import pandas as pd
        df = pd.DataFrame(runs)
        df["readiness"] = (df["score"] / df["max_score"] * 100).round(0).astype(int).astype(str) + "%"
        st.dataframe(
            df[["ts", "scenario_name", "score", "max_score", "readiness"]].sort_values("ts", ascending=False),
            use_container_width=True, hide_index=True,
        )
    else:
        st.caption("No drills run yet.")
