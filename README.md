<div align="center">

# ✅ To-Do App

**A multi-user task manager with authentication, built with Streamlit, PostgreSQL and SQLAlchemy.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Tests](https://github.com/Aivalio/todo-app/actions/workflows/tests.yml/badge.svg)](https://github.com/Aivalio/todo-app/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📖 About

A full-stack To-Do application where each user manages their own private task list.
Built as a portfolio project to practice **authentication**, **relational databases**,
and **clean layered architecture** in Python.

**Every task is scoped to its owner.** Users can never see or modify each other's data —
this is enforced at the service layer, not just the UI.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **User Authentication** | Register + login with bcrypt-hashed passwords |
| 👤 **Per-User Isolation** | Each user sees only their own tasks |
| ➕ **Task CRUD** | Create, read, update, delete tasks |
| 🎯 **Priority Levels** | Low / Medium / High, sorted automatically |
| 📅 **Due Dates** | Optional deadlines |
| ✅ **Completion Toggle** | One-click checkbox with strikethrough styling |
| 🔍 **Filters & Search** | By status, priority, or text in title/description |
| 📊 **Live Stats** | Total / done / pending counts + priority breakdown |
| ⚙️ **Secure Config** | Credentials loaded from `.env`, never committed |

---

## 🏗️ Architecture

Layered architecture following the **Single Responsibility Principle**:


**Why this matters:**
- The **UI** knows nothing about the database.
- The **services** know nothing about Streamlit.
- The **models** define structure, not behavior.
- Every layer is independently testable.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **UI** | Streamlit | Rapid, interactive web app |
| **ORM** | SQLAlchemy 2.0 | Typed, modern Python DB layer |
| **Database** | PostgreSQL (Supabase) | Cloud-hosted relational DB |
| **Auth** | passlib + bcrypt | Password hashing |
| **Config** | python-dotenv | Secret management |
| **Tests** | pytest | 38 unit tests, in-memory SQLite |
| **Deploy** | Streamlit Cloud | Free hosting from GitHub |

---

## 🚀 Live Demo

👉 **https://todo-app-aivalio.streamlit.app/**

## 📸 Screenshots

| Login                                | Register                                   |
|--------------------------------------|--------------------------------------------|
| ![Login](docs/screenshots/login.jpg) | ![Register](docs/screenshots/register.jpg) |

| Task List (authenticated)            |
|--------------------------------------|
| ![Tasks](docs/screenshots/tasks.jpg) |


## 📦 Installation

### Prerequisites

- Python 3.11+
- A free [Supabase](https://supabase.com) account (for the PostgreSQL DB)

### 1. Clone

```bash
git clone https://github.com/Aivalio/todo-app.git
cd todo-app
```


### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure secrets

```bash
# Windows
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` and paste your Supabase **Transaction Pooler** connection string:

```
DATABASE_URL=postgresql://postgres.PROJECT_ID:your_password@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

> ⚠️ **Never commit `.env`.** It is ignored by Git.
>
> 💡 **Use the Transaction Pooler** (port `6543`), not the Direct connection.

### 5. Initialize the database

```bash
python -c "from src.database import init_db; init_db(); print('Tables created')"
```

### 6. Run the app

```bash
streamlit run src/app.py
```

Open http://localhost:8501

---

## 🧪 Testing

```bash
pytest tests/ -v
```

**Coverage:** 38 tests, all mocked with in-memory SQLite.

| Module | What's tested |
|---|---|
| `auth_service` | Hashing, verification, registration, duplicate detection, login |
| `task_service` | CRUD, priority sorting, filtering, search, cross-user isolation |

**Test design:**

- **In-memory SQLite** → instant, isolated per test, no cleanup
- **Fixtures in `conftest.py`** → shared setup, no duplication
- **User isolation tests** → every service test that touches data checks cross-user access

---

## 📁 Project Structure

```
todo-app/
├── src/
│   ├── __init__.py
│   ├── app.py                       # Streamlit entry + router
│   ├── config.py                    # Env var loader
│   ├── database.py                  # Engine + session + Base
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                  # User model
│   │   └── task.py                  # Task model (FK → User)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py          # Register, login, hashing
│   │   └── task_service.py          # Task CRUD, filters, stats
│   └── ui/
│       ├── __init__.py
│       ├── auth_ui.py               # Login/Register pages
│       └── task_ui.py               # Task list + sidebar + forms
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # SQLite fixtures
│   ├── test_auth_service.py
│   └── test_task_service.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🔐 Security Notes

- **Passwords** are hashed with `bcrypt` — never stored in plain text.
- **Secrets** live in `.env` and are never committed.
- **Cross-user access** is prevented at the service layer:

```python
def get_task(session, task_id, user_id):
    return session.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id,  # ← not just task_id
    ).first()
```

Even if an attacker guesses a valid task ID, they cannot access it.

---

## 🗺️ Roadmap

- [ ] Alembic migrations (instead of `create_all`)
- [ ] Password reset via email
- [ ] Task categories / tags
- [ ] Recurring tasks
- [ ] Docker + docker-compose for self-hosting
- [ ] REST API endpoints (FastAPI)

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<div align="center">

**Built with ☕ and curiosity by [Aivalio](https://github.com/Aivalio)**

⭐ If you found this useful, consider giving it a star!

</div>

