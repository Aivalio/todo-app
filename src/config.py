"""Configuration loader for environment variables."""
import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """Retrieve the PostgreSQL connection string.

    Tries Streamlit secrets first (for deployed app), then falls back
    to the DATABASE_URL environment variable (for local dev and tests).

    Returns:
        The database connection string.

    Raises:
        ValueError: If neither source provides a URL.
    """
    # Try Streamlit secrets (only available when running under Streamlit)
    try:
        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except Exception:
        pass  # Not running under Streamlit, or no secrets file

    # Fall back to environment variable
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    raise ValueError(
        "DATABASE_URL is not set. "
        "Configure .streamlit/secrets.toml or a DATABASE_URL env var."
    )