import sqlite3
import json
import os
from contextlib import contextmanager
from datetime import datetime

DB_PATH = os.environ.get(
    "TRADEGUARD_DB_PATH", os.path.join(os.path.dirname(__file__), "tradeguard.db")
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS ai_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    system_type TEXT NOT NULL,
    description TEXT,
    autonomy_level TEXT,
    risk_classification TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    model_name TEXT,
    purpose TEXT,
    training_data_disclosed TEXT,
    data_retention TEXT,
    audit_rights_in_contract TEXT,
    region TEXT,
    risk_score INTEGER,
    risk_tier TEXT,
    notes TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_name TEXT,
    ts TEXT,
    ticker TEXT,
    decision TEXT,
    inputs_json TEXT,
    explanation TEXT,
    confidence REAL
);

CREATE TABLE IF NOT EXISTS redteam_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    attack_id TEXT,
    attack_name TEXT,
    category TEXT,
    payload TEXT,
    response TEXT,
    verdict TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    scenario_id TEXT,
    scenario_name TEXT,
    score INTEGER,
    max_score INTEGER,
    answers_json TEXT,
    aar TEXT
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        cur = conn.execute("SELECT COUNT(*) AS c FROM ai_systems")
        if cur.fetchone()["c"] == 0:
            _seed(conn)


def _seed(conn):
    now = datetime.utcnow().isoformat()

    systems = [
        ("Momentum Signal Engine", "signal_generator",
         "Rule-based + ML momentum signal generator for equity swing trades.",
         "Autonomous (auto-executes below $250k notional)", "High", now),
        ("Wealth Copilot", "research_copilot",
         "LLM-powered assistant for advisors; drafts client research notes, has read access to positions.",
         "Human-in-the-loop", "Medium", now),
        ("RoboAdvise Lite", "robo_advisor",
         "Automated portfolio rebalancing and recommendations for retail clients.",
         "Autonomous (executes rebalances directly)", "High", now),
        ("Smart Order Router", "execution_algo",
         "Execution-only algo that splits and routes orders across venues.",
         "Autonomous (execution only, no investment decisions)", "Low", now),
    ]
    conn.executemany(
        "INSERT INTO ai_systems (name, system_type, description, autonomy_level, risk_classification, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        systems,
    )

    vendors = [
        ("Anthropic", "Claude (API)", "Wealth Copilot research drafting", "Documented (usage policy published)",
         "Not used for training per API terms", "Yes - enterprise agreement", "US/EU", 25, "Low",
         "Vendor publishes model card and usage policy.", now),
        ("OpenAI", "GPT-4 class (API)", "Client chat support prototype", "Documented (usage policy published)",
         "Not used for training per API terms", "Unclear - standard ToS only", "US", 45, "Medium",
         "No negotiated audit rights yet; flagged for legal review.", now),
        ("DataFeedX", "Proprietary alt-data model", "Alternative data signals feeding Momentum Signal Engine",
         "Not disclosed", "Unknown", "No", "Unknown", 80, "High",
         "Vendor won't disclose training data or model architecture. No incident history on file.", now),
        ("In-House Quant Team", "LSTM-v3 (internal)", "Core momentum signal model", "Fully documented (internal)",
         "N/A - internal", "N/A - internal", "US", 15, "Low",
         "Internal model, full lineage tracked in MLflow.", now),
    ]
    conn.executemany(
        "INSERT INTO vendors (name, model_name, purpose, training_data_disclosed, data_retention, "
        "audit_rights_in_contract, region, risk_score, risk_tier, notes, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        vendors,
    )


def insert_audit_entry(system_name, ticker, decision, inputs, explanation, confidence):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO audit_log (system_name, ts, ticker, decision, inputs_json, explanation, confidence) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (system_name, datetime.utcnow().isoformat(), ticker, decision,
             json.dumps(inputs), explanation, confidence),
        )


def fetch_audit_log(limit=200):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def insert_redteam_run(attack_id, attack_name, category, payload, response, verdict, notes=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO redteam_runs (ts, attack_id, attack_name, category, payload, response, verdict, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), attack_id, attack_name, category, payload, response, verdict, notes),
        )


def fetch_redteam_runs(limit=200):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM redteam_runs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def insert_incident_run(scenario_id, scenario_name, score, max_score, answers, aar):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO incidents (ts, scenario_id, scenario_name, score, max_score, answers_json, aar) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), scenario_id, scenario_name, score, max_score,
             json.dumps(answers), aar),
        )


def fetch_incident_runs(limit=200):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM incidents ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def fetch_vendors():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM vendors ORDER BY risk_score DESC").fetchall()
        return [dict(r) for r in rows]


def insert_vendor(name, model_name, purpose, training_data_disclosed, data_retention,
                   audit_rights_in_contract, region, risk_score, risk_tier, notes):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO vendors (name, model_name, purpose, training_data_disclosed, data_retention, "
            "audit_rights_in_contract, region, risk_score, risk_tier, notes, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, model_name, purpose, training_data_disclosed, data_retention,
             audit_rights_in_contract, region, risk_score, risk_tier, notes,
             datetime.utcnow().isoformat()),
        )


def fetch_ai_systems():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM ai_systems ORDER BY id").fetchall()
        return [dict(r) for r in rows]
