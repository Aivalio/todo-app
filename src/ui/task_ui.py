"""Streamlit UI for managing tasks."""
from datetime import date

import streamlit as st
from sqlalchemy.orm import Session

from src.services.task_service import (
    create_task,
    delete_task,
    get_stats,
    get_tasks,
    toggle_complete,
    update_task,
)


PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def _render_sidebar(session: Session) -> None:
    """Render sidebar: user info, stats, logout."""
    user_id = st.session_state.user_id

    with st.sidebar:
        st.header(f"👤 {st.session_state.username}")

        stats = get_stats(session, user_id)
        st.metric("Total tasks", stats["total"])
        col1, col2 = st.columns(2)
        col1.metric("Done", stats["completed"])
        col2.metric("Pending", stats["pending"])

        st.divider()
        st.caption("By priority")
        for p, count in stats["by_priority"].items():
            st.write(f"{PRIORITY_EMOJI[p]} {p.capitalize()}: {count}")

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.pop("user_id", None)
            st.session_state.pop("username", None)
            st.rerun()


def _render_add_form(session: Session) -> None:
    """Render the 'add task' form."""
    with st.expander("➕ Add a new task", expanded=False):
        with st.form("add_task_form", clear_on_submit=True):
            title = st.text_input("Title", max_chars=200)
            description = st.text_area("Description", height=68)
            col1, col2 = st.columns(2)
            priority = col1.selectbox("Priority", ["low", "medium", "high"], index=1)
            due = col2.date_input("Due date", value=None)

            submit = st.form_submit_button("Add task", use_container_width=True)

            if submit:
                try:
                    create_task(
                        session,
                        user_id=st.session_state.user_id,
                        title=title,
                        description=description,
                        priority=priority,
                        due_date=due,
                    )
                    st.success(f"Added: {title}")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


def _render_filters() -> dict:
    """Render filter controls and return the active filter values."""
    col1, col2, col3 = st.columns([1, 1, 2])
    status = col1.selectbox("Status", ["All", "Pending", "Completed"])
    priority = col2.selectbox("Priority", ["All", "low", "medium", "high"])
    search = col3.text_input("🔍 Search", placeholder="Search title or description...")

    filters = {
        "completed": {"All": None, "Pending": False, "Completed": True}[status],
        "priority": None if priority == "All" else priority,
        "search": search.strip() if search else None,
    }
    return filters


def _render_task_row(session: Session, task) -> None:
    """Render a single task row with checkbox and actions."""
    user_id = st.session_state.user_id

    col_check, col_body, col_actions = st.columns([0.5, 5, 1.5])

    with col_check:
        checked = st.checkbox(
            "",
            value=task.completed,
            key=f"chk_{task.id}",
            label_visibility="collapsed",
        )
        if checked != task.completed:
            toggle_complete(session, task.id, user_id)
            st.rerun()

    with col_body:
        emoji = PRIORITY_EMOJI.get(task.priority, "⚪")
        title_style = "~~" if task.completed else ""
        st.markdown(f"{emoji} **{title_style}{task.title}{title_style}**")
        if task.description:
            st.caption(task.description)
        meta = []
        if task.due_date:
            meta.append(f"📅 {task.due_date.strftime('%Y-%m-%d')}")
        meta.append(f"Priority: {task.priority}")
        st.caption(" • ".join(meta))

    with col_actions:
        edit_key = f"edit_{task.id}"
        delete_key = f"del_{task.id}"

        if st.button("✏️", key=edit_key, help="Edit"):
            st.session_state[f"editing_{task.id}"] = True

        if st.button("🗑️", key=delete_key, help="Delete"):
            if delete_task(session, task.id, user_id):
                st.rerun()

    # Edit form (shown inline if editing)
    if st.session_state.get(f"editing_{task.id}"):
        with st.form(f"edit_form_{task.id}"):
            new_title = st.text_input("Title", value=task.title)
            new_desc = st.text_area("Description", value=task.description or "")
            new_priority = st.selectbox(
                "Priority",
                ["low", "medium", "high"],
                index=["low", "medium", "high"].index(task.priority),
            )
            new_due = st.date_input(
                "Due date",
                value=task.due_date.date() if task.due_date else None,
            )
            col_save, col_cancel = st.columns(2)
            save = col_save.form_submit_button("💾 Save", use_container_width=True)
            cancel = col_cancel.form_submit_button("❌ Cancel", use_container_width=True)

            if save:
                try:
                    update_task(
                        session, task.id, user_id,
                        title=new_title,
                        description=new_desc,
                        priority=new_priority,
                        due_date=new_due,
                    )
                    del st.session_state[f"editing_{task.id}"]
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
            if cancel:
                del st.session_state[f"editing_{task.id}"]
                st.rerun()


def render_task_page(session: Session) -> None:
    """Render the main task page."""
    _render_sidebar(session)

    st.title("📝 My Tasks")

    _render_add_form(session)

    st.divider()

    filters = _render_filters()
    tasks = get_tasks(session, st.session_state.user_id, **filters)

    if not tasks:
        st.info("No tasks match your filters. Add one above!")
        return

    st.caption(f"Showing **{len(tasks)}** task(s)")
    for task in tasks:
        _render_task_row(session, task)
        st.divider()