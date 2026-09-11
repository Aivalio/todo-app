"""Tests for the task service."""
import pytest

from src.services.task_service import (
    create_task,
    delete_task,
    get_stats,
    get_task,
    get_tasks,
    toggle_complete,
    update_task,
)


# --- Create ---

def test_create_task_success(session, sample_user):
    task = create_task(session, sample_user.id, "Buy milk", priority="high")
    assert task.id is not None
    assert task.title == "Buy milk"
    assert task.priority == "high"
    assert task.completed is False
    assert task.user_id == sample_user.id


def test_create_task_trims_title(session, sample_user):
    task = create_task(session, sample_user.id, "   Buy milk   ")
    assert task.title == "Buy milk"


def test_create_task_empty_title_raises(session, sample_user):
    with pytest.raises(ValueError, match="cannot be empty"):
        create_task(session, sample_user.id, "   ")


def test_create_task_invalid_priority_raises(session, sample_user):
    with pytest.raises(ValueError, match="Priority must be one of"):
        create_task(session, sample_user.id, "Buy milk", priority="urgent")


# --- Read ---

def test_get_task_returns_own_task(session, sample_user):
    task = create_task(session, sample_user.id, "Buy milk")
    assert get_task(session, task.id, sample_user.id).id == task.id


def test_get_task_returns_none_for_other_user(session, sample_user, second_user):
    task = create_task(session, sample_user.id, "Buy milk")
    assert get_task(session, task.id, second_user.id) is None


def test_get_tasks_only_returns_own_tasks(session, sample_user, second_user):
    create_task(session, sample_user.id, "Alice task")
    create_task(session, second_user.id, "Bob task")

    alice_tasks = get_tasks(session, sample_user.id)
    assert len(alice_tasks) == 1
    assert alice_tasks[0].title == "Alice task"


def test_get_tasks_filter_by_completed(session, sample_user):
    t1 = create_task(session, sample_user.id, "Pending task")
    t2 = create_task(session, sample_user.id, "Done task")
    toggle_complete(session, t2.id, sample_user.id)

    pending = get_tasks(session, sample_user.id, completed=False)
    completed = get_tasks(session, sample_user.id, completed=True)

    assert [t.title for t in pending] == ["Pending task"]
    assert [t.title for t in completed] == ["Done task"]


def test_get_tasks_filter_by_priority(session, sample_user):
    create_task(session, sample_user.id, "Low task", priority="low")
    create_task(session, sample_user.id, "High task", priority="high")

    highs = get_tasks(session, sample_user.id, priority="high")
    assert len(highs) == 1
    assert highs[0].title == "High task"


def test_get_tasks_search_in_title_and_description(session, sample_user):
    create_task(session, sample_user.id, "Buy milk", description="from the store")
    create_task(session, sample_user.id, "Walk dog", description="in the park")

    results = get_tasks(session, sample_user.id, search="milk")
    assert len(results) == 1
    assert results[0].title == "Buy milk"

    results = get_tasks(session, sample_user.id, search="park")
    assert len(results) == 1
    assert results[0].title == "Walk dog"


def test_get_tasks_sorted_by_priority(session, sample_user):
    create_task(session, sample_user.id, "Low", priority="low")
    create_task(session, sample_user.id, "High", priority="high")
    create_task(session, sample_user.id, "Medium", priority="medium")

    tasks = get_tasks(session, sample_user.id)
    assert [t.priority for t in tasks] == ["high", "medium", "low"]


# --- Update ---

def test_update_task_own_task(session, sample_user):
    task = create_task(session, sample_user.id, "Old title")
    updated = update_task(session, task.id, sample_user.id, title="New title")
    assert updated is not None
    assert updated.title == "New title"


def test_update_task_other_users_task_returns_none(session, sample_user, second_user):
    task = create_task(session, sample_user.id, "Alice task")
    result = update_task(session, task.id, second_user.id, title="Hacked")
    assert result is None


def test_update_task_invalid_field_raises(session, sample_user):
    task = create_task(session, sample_user.id, "Task")
    with pytest.raises(ValueError, match="Cannot update field"):
        update_task(session, task.id, sample_user.id, username="hacker")


def test_toggle_complete(session, sample_user):
    task = create_task(session, sample_user.id, "Task")
    assert task.completed is False

    updated = toggle_complete(session, task.id, sample_user.id)
    assert updated.completed is True

    updated = toggle_complete(session, task.id, sample_user.id)
    assert updated.completed is False


def test_toggle_complete_other_users_task_returns_none(session, sample_user, second_user):
    task = create_task(session, sample_user.id, "Task")
    assert toggle_complete(session, task.id, second_user.id) is None


# --- Delete ---

def test_delete_task_own_task(session, sample_user):
    task = create_task(session, sample_user.id, "Task")
    assert delete_task(session, task.id, sample_user.id) is True
    assert get_task(session, task.id, sample_user.id) is None


def test_delete_task_other_users_task_returns_false(session, sample_user, second_user):
    task = create_task(session, sample_user.id, "Alice task")
    assert delete_task(session, task.id, second_user.id) is False
    assert get_task(session, task.id, sample_user.id) is not None


# --- Stats ---

def test_get_stats_empty(session, sample_user):
    stats = get_stats(session, sample_user.id)
    assert stats == {
        "total": 0,
        "completed": 0,
        "pending": 0,
        "by_priority": {"low": 0, "medium": 0, "high": 0},
    }


def test_get_stats_with_tasks(session, sample_user):
    t1 = create_task(session, sample_user.id, "A", priority="high")
    t2 = create_task(session, sample_user.id, "B", priority="medium")
    create_task(session, sample_user.id, "C", priority="low")
    toggle_complete(session, t1.id, sample_user.id)

    stats = get_stats(session, sample_user.id)
    assert stats["total"] == 3
    assert stats["completed"] == 1
    assert stats["pending"] == 2
    assert stats["by_priority"] == {"low": 1, "medium": 1, "high": 1}