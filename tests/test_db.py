import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_seed_data_present(temp_db):
    assert len(temp_db.fetch_ai_systems()) == 4
    assert len(temp_db.fetch_vendors()) == 4


def test_insert_and_fetch_audit_entry(temp_db):
    temp_db.insert_audit_entry("TestSystem", "TEST", "BUY", {"x": 1}, "because reasons", 0.8)
    entries = temp_db.fetch_audit_log()
    assert len(entries) == 1
    assert entries[0]["ticker"] == "TEST"
    assert entries[0]["decision"] == "BUY"


def test_insert_and_fetch_redteam_run(temp_db):
    temp_db.insert_redteam_run("id1", "Test Attack", "LLM01", "payload", "response", "BLOCKED", "notes")
    runs = temp_db.fetch_redteam_runs()
    assert len(runs) == 1
    assert runs[0]["verdict"] == "BLOCKED"


def test_insert_and_fetch_vendor(temp_db):
    temp_db.insert_vendor(
        "NewVendor", "Model X", "purpose", "Not disclosed", "Unknown", "No", "Unknown", 90, "Critical", "note"
    )
    vendors = temp_db.fetch_vendors()
    assert any(v["name"] == "NewVendor" for v in vendors)


def test_insert_and_fetch_incident_run(temp_db):
    temp_db.insert_incident_run("scenario1", "Test Scenario", 3, 4, ["a", "b", "c", "d"], "AAR text")
    runs = temp_db.fetch_incident_runs()
    assert len(runs) == 1
    assert runs[0]["score"] == 3
