"""Streamlit UI for login and registration."""
import streamlit as st
from sqlalchemy.orm import Session

from src.services.auth_service import register_user, authenticate


def render_login(session: Session) -> None:
    """Render the login form. On success, stores user in session_state."""
    st.subheader("🔐 Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)

    if submit:
        if not username or not password:
            st.warning("Please fill in all fields.")
            return

        user = authenticate(session, username, password)
        if user is None:
            st.error("Invalid username or password.")
            return

        st.session_state.user_id = user.id
        st.session_state.username = user.username
        st.rerun()


def render_register(session: Session) -> None:
    """Render the registration form. On success, logs the user in."""
    st.subheader("📝 Register")

    with st.form("register_form"):
        username = st.text_input("Username", help="At least 3 characters")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password", help="At least 6 characters")
        confirm = st.text_input("Confirm password", type="password")
        submit = st.form_submit_button("Create account", use_container_width=True)

    if submit:
        if password != confirm:
            st.error("Passwords do not match.")
            return

        try:
            user = register_user(session, username, email, password)
        except ValueError as e:
            st.error(str(e))
            return

        st.session_state.user_id = user.id
        st.session_state.username = user.username
        st.rerun()


def render_auth_page(session: Session) -> None:
    """Render the full auth page with tabs."""
    st.title("✅ To-Do App")
    st.caption("Organize your tasks, one day at a time.")

    tab_login, tab_register = st.tabs(["Login", "Register"])
    with tab_login:
        render_login(session)
    with tab_register:
        render_register(session)


def logout() -> None:
    """Clear the current session and rerun."""
    st.session_state.pop("user_id", None)
    st.session_state.pop("username", None)
    st.rerun()