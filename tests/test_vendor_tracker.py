import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import vendor_tracker
from data.regulatory_mapping import risk_tier_from_score, suggest_frameworks


def test_best_case_vendor_scores_zero():
    score = vendor_tracker._compute_risk_score(
        "Fully documented (internal)", "N/A - internal", "Yes - enterprise agreement", "US"
    )
    assert score == 0
    assert risk_tier_from_score(score) == "Low"


def test_worst_case_vendor_scores_high():
    score = vendor_tracker._compute_risk_score("Not disclosed", "Unknown", "No", "Unknown")
    assert score >= 70
    assert risk_tier_from_score(score) == "Critical"


def test_score_is_capped_at_100():
    score = vendor_tracker._compute_risk_score("not disclosed", "unknown", "no", "unknown")
    assert score <= 100


def test_suggest_frameworks_always_includes_baseline():
    frameworks = suggest_frameworks("execution_algo", "Autonomous execution only", "US")
    assert "finra-3110" in frameworks
    assert "sec-2026-priorities" in frameworks
    assert "treasury-fs-ai-rmf" in frameworks


def test_suggest_frameworks_flags_eu_ai_act_for_robo_advisor():
    frameworks = suggest_frameworks("robo_advisor", "Autonomous", "EU")
    assert "eu-ai-act-annex3" in frameworks
