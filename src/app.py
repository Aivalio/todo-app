"""Streamlit entry point: routes between auth page and task page."""
import sys
from pathlib import Path

# Make project root importable when running `streamlit run src/app.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.database import get_session
from src.ui.auth_ui import render_auth_page, logout


st.set_page_config(
    page_title="To-Do App",
    page_icon="✅",
    layout="centered",
)


if "user_id" not in st.session_state:
    st.session_state.user_id = None


session = next(get_session())


if st.session_state.user_id is None:
    render_auth_page(session)
else:
    st.title("✅ To-Do App")
    st.success(f"You are logged in as **{st.session_state.username}**")

    if st.button("Logout"):
        logout()

    st.divider()
    st.info("🚧 Task UI coming in the next branch.")