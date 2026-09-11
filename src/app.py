"""Streamlit entry point: routes between auth page and task page."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.database import get_session
from src.ui.auth_ui import render_auth_page


st.set_page_config(
    page_title="To-Do App",
    page_icon="✅",
    layout="wide",  # ← αλλάζουμε σε wide για τα 2 columns
)


if "user_id" not in st.session_state:
    st.session_state.user_id = None


session = next(get_session())


if st.session_state.user_id is None:
    render_auth_page(session)
else:
    from src.ui.task_ui import render_task_page
    render_task_page(session)