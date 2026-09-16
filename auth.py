"""
TradeGuard - minimal access-control gate.

This is intentionally simple (a single shared password), not a real
multi-user auth system. It exists to close the most obvious version of
the "no access control" gap: as shipped, this app would otherwise be
wide open to anyone who reaches the URL. For a real deployment, this
should be replaced with proper per-user authentication and role-based
access control (see README.md "Notes and limitations").
"""
import os

import streamlit as st

DEFAULT_PASSWORD = "tradeguard-demo"


def _get_password() -> str:
    return os.environ.get("TRADEGUARD_PASSWORD", DEFAULT_PASSWORD)


def require_login():
    """Blocks the rest of the app until the correct password is entered.
    Call this once, near the top of app.py, before rendering any page."""
    if st.session_state.get("authenticated"):
        return

    st.title("🛡️ TradeGuard")
    st.caption("Enter the access password to continue.")

    password = _get_password()
    if password == DEFAULT_PASSWORD:
        st.info(
            f"No `TRADEGUARD_PASSWORD` environment variable is set, so the default demo "
            f"password is in use: `{DEFAULT_PASSWORD}`. Set `TRADEGUARD_PASSWORD` before "
            f"deploying this anywhere it isn't just you testing locally."
        )

    entered = st.text_input("Password", type="password")
    if st.button("Enter", type="primary"):
        if entered == password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")

    st.stop()
