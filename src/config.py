import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """Retrieve PostgreSQL connection string from Streamlit secrets or env vars."""
    # 1. Πρώτα ελέγχει αν υπάρχει ορισμένο στο Streamlit Cloud Secrets
    if "DATABASE_URL" in st.secrets:
        return st.secrets["DATABASE_URL"]

    # 2. Αν δεν υπάρχει, ελέγχει τις περιβαλλοντικές μεταβλητές (τοπικό .env)
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    raise ValueError(
        "DATABASE_URL not set. "
        "Please set DATABASE_URL in Streamlit Cloud Secrets or in your local .env file."
    )
    
