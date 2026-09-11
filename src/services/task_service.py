"""Task service: CRUD operations scoped per user."""
from datetime import datetime
from sqlalchemy.orm import Session
from src.models import Task


# Allowed priority levels
VALID_PRIORITIES = ("low", "medium", "high")

# Fields that can be updated via update_task()
UPDATABLE_FIELDS = ("title", "description", "priority", "due_date", "completed")


# --- Create ---

def create_task(
    session: Session,
    user_id: int,
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: datetime | None = None,
) -> Task:
    """Create a new task for a user.

    Args:
        session: Database session.
        user_id: Owner of the task.
        title: Task title (required, max 200 chars).
        description: Optional details.
        priority: One of 'low', 'medium', 'high'.
        due_date: Optional due date.

    Returns:
        The newly created Task.

    Raises:
        ValueError: If title is empty or priority is invalid.
    """
    title = title.strip()
    if not title:
        raise ValueError("Task title cannot be empty.")
    if len(title) > 200:
        raise ValueError("Task title must be 200 characters or fewer.")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Priority must be one of {VALID_PRIORITIES}.")

    task = Task(
        user_id=user_id,
        title=title,
        description=description.strip(),
        priority=priority,
        due_date=due_date,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# --- Read ---

def get_task(session: Session, task_id: int, user_id: int) -> Task | None:
    """Fetch a single task, ensuring it belongs to the user.

    Args:
        session: Database session.
        task_id: Task primary key.
        user_id: Owner (for scoping).

    Returns:
        The Task or None if not found / not owned.
    """
    return (
        session.query(Task)
        .filter(Task.id == task_id, Task.user_id == user_id)
        .first()
    )


def get_tasks(
    session: Session,
    user_id: int,
    *,
    completed: bool | None = None,
    priority: str | None = None,
    search: str | None = None,
) -> list[Task]:
    """Fetch all tasks for a user, with optional filters.

    Args:
        session: Database session.
        user_id: Owner of the tasks.
        completed: Filter by completion status (None = all).
        priority: Filter by priority level.
        search: Substring to search in title/description.

    Returns:
        List of Task objects, ordered by priority (high first), due_date, created_at.
    """
    query = session.query(Task).filter(Task.user_id == user_id)

    if completed is not None:
        query = query.filter(Task.completed == completed)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Task.title.ilike(pattern)) | (Task.description.ilike(pattern))
        )

    # Order: high priority first, then by due date, then by creation
    priority_order = {"high": 0, "medium": 1, "low": 2}
    tasks = query.all()
    tasks.sort(
        key=lambda t: (
            priority_order.get(t.priority, 1),
            t.due_date or datetime.max,
            t.created_at,
        )
    )
    return tasks


# --- Update ---

def update_task(
    session: Session,
    task_id: int,
    user_id: int,
    **fields,
) -> Task | None:
    """Update a task's fields.

    Args:
        session: Database session.
        task_id: Task primary key.
        user_id: Owner (for scoping).
        **fields: Fields to update (title, description, priority, due_date, completed).

    Returns:
        The updated Task, or None if not found / not owned.

    Raises:
        ValueError: If an invalid field or value is provided.
    """
    task = get_task(session, task_id, user_id)
    if task is None:
        return None

    for key, value in fields.items():
        if key not in UPDATABLE_FIELDS:
            raise ValueError(f"Cannot update field '{key}'.")
        if key == "title":
            value = value.strip()
            if not value:
                raise ValueError("Task title cannot be empty.")
        if key == "priority" and value not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of {VALID_PRIORITIES}.")
        setattr(task, key, value)

    session.commit()
    session.refresh(task)
    return task


def toggle_complete(session: Session, task_id: int, user_id: int) -> Task | None:
    """Toggle the completion status of a task.

    Args:
        session: Database session.
        task_id: Task primary key.
        user_id: Owner (for scoping).

    Returns:
        The updated Task, or None if not found / not owned.
    """
    task = get_task(session, task_id, user_id)
    if task is None:
        return None
    task.completed = not task.completed
    session.commit()
    session.refresh(task)
    return task


# --- Delete ---

def delete_task(session: Session, task_id: int, user_id: int) -> bool:
    """Delete a task.

    Args:
        session: Database session.
        task_id: Task primary key.
        user_id: Owner (for scoping).

    Returns:
        True if deleted, False if not found / not owned.
    """
    task = get_task(session, task_id, user_id)
    if task is None:
        return False
    session.delete(task)
    session.commit()
    return True


# --- Statistics ---

def get_stats(session: Session, user_id: int) -> dict:
    """Return summary statistics for a user's tasks.

    Args:
        session: Database session.
        user_id: Owner of the tasks.

    Returns:
        Dict with total, completed, pending, and counts by priority.
    """
    tasks = get_tasks(session, user_id)
    total = len(tasks)
    completed = sum(1 for t in tasks if t.completed)
    by_priority = {"low": 0, "medium": 0, "high": 0}
    for t in tasks:
        by_priority[t.priority] = by_priority.get(t.priority, 0) + 1

    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
        "by_priority": by_priority,
    }