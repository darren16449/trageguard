import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db as db_module


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Points db.py at a throwaway SQLite file for the duration of one test,
    so tests never touch (or depend on) the real tradeguard.db."""
    db_path = str(tmp_path / "test_tradeguard.db")
    monkeypatch.setattr(db_module, "DB_PATH", db_path)
    db_module.init_db()
    return db_module
