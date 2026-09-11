"""Configuration loader for environment variables."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_database_url() -> str:
    """Retrieve the PostgreSQL connection string from environment variables.

    Returns:
        str: The DATABASE_URL.

    Raises:
        ValueError: If DATABASE_URL is not set.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError(
            "DATABASE_URL not set. "
            "Copy .env.example to .env and add your connection string."
        )
    return url