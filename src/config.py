import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """Retrieve PostgreSQL connection string from Streamlit secrets or env vars."""
    if "DATABASE_URL" in st.secrets:
        return st.secrets["DATABASE_URL"]

    url = os.getenv("DATABASE_URL")
    if url:
        return url

    raise ValueError("DATABASE_URL is not set.")
    
