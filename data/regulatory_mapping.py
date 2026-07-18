"""
Regulatory reference data used by the vendor/model provenance tracker.
Sourced from research conducted July 2026 - see README.md 'Sources' for links.
This is an educational reference mapping, not legal advice.
"""

FRAMEWORKS = [
    {
        "id": "finra-3110",
        "name": "FINRA Rule 3110 (Supervision)",
        "summary": "FINRA has not issued AI-specific rules; existing supervision, recordkeeping, "
                    "communications, and fair-dealing rules are applied as 'technology neutral' to "
                    "AI/GenAI use. The 2026 FINRA Annual Regulatory Oversight Report notes a 5x jump "
                    "in member-reported AI use cases (3 in 2025 to 15 in 2026) and recommends firms "
                    "supervise GenAI at both individual and enterprise levels.",
        "applies_when": "Any AI system used by a FINRA member firm, especially those touching "
                         "communications, recordkeeping, or trading supervision.",
    },
    {
        "id": "sec-2026-priorities",
        "name": "SEC 2026 Examination Priorities (AI governance)",
        "summary": "The SEC withdrew its 2023 predictive data analytics proposal in 2025 with no "
                    "substitute rule. Its 2026 exam priorities instead focus on whether firms have "
                    "'adequate policies and procedures to monitor and/or supervise their use of AI "
                    "technologies' - i.e., governance process is the exam target, not a specific AI rule.",
        "applies_when": "Any registered investment adviser or broker-dealer using AI in client-facing "
                         "or investment-decision workflows.",
    },
    {
        "id": "eu-ai-act-annex3",
        "name": "EU AI Act, Annex III(5)(b) - High-Risk Creditworthiness/Financial Systems",
        "summary": "AI systems that evaluate creditworthiness or credit scores of natural persons are "
                    "explicitly high-risk. Robo-advisors may qualify as high-risk if they score a "
                    "client's financial capacity or make autonomous decisions affecting a person's "
                    "access to financial services. Pure execution algorithms (routing/market-making) "
                    "are likely minimal-risk. NOTE: the original 2 August 2026 deadline for these "
                    "obligations was postponed by the EU's AI Act 'Digital Omnibus' (final approval "
                    "29 June 2026) - standalone high-risk Annex III systems now have until "
                    "2 December 2027 to comply. Verify the current date against official EU sources, "
                    "as this timeline has already moved once.",
        "applies_when": "Robo-advisors, credit/affordability scoring, or any AI making autonomous "
                         "investment decisions that affect a natural person's assets or access to "
                         "financial services, especially serving EU clients.",
    },
    {
        "id": "treasury-fs-ai-rmf",
        "name": "Treasury Financial Services AI Risk Management Framework (FS AI RMF)",
        "summary": "Released Feb 2026 by the U.S. Treasury with the Cyber Risk Institute, built on the "
                    "NIST AI RMF's four functions (Govern, Map, Measure, Manage) with ~230 control "
                    "objectives tailored to financial services, including a dedicated third-party/vendor "
                    "risk section.",
        "applies_when": "Any financial institution wanting a structured, voluntary framework to "
                         "organize AI governance - especially useful for vendor/third-party risk review.",
    },
]


def suggest_frameworks(system_type: str, autonomy_level: str, region: str) -> list[str]:
    """Very simple rule-based mapper from a vendor/system profile to applicable frameworks."""
    ids = ["finra-3110", "sec-2026-priorities"]  # baseline for any US financial AI use
    text = f"{system_type} {autonomy_level}".lower()
    if any(k in text for k in ["robo", "credit", "advisor", "autonomous"]):
        ids.append("eu-ai-act-annex3")
    ids.append("treasury-fs-ai-rmf")
    return ids


def risk_tier_from_score(score: int) -> str:
    if score >= 70:
        return "Critical"
    if score >= 45:
        return "High"
    if score >= 20:
        return "Medium"
    return "Low"
