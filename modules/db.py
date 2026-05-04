import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None


def _read_setting(key: str, default: str | None = None) -> str | None:
    """Read config from environment first, then Streamlit secrets."""
    value = os.getenv(key)
    if value:
        return value.replace("\\n", "").strip()

    try:
        import streamlit as st

        secret_val = st.secrets.get(key)
        if secret_val:
            return str(secret_val).replace("\\n", "").strip()
    except Exception:
        pass

    return default


def get_db():
    global _client

    mongodb_uri = _read_setting("MONGODB_URI")
    mongodb_db = _read_setting("MONGODB_DB", "scrapsenseai")

    if _client is None:
        if not mongodb_uri:
            raise ValueError("MONGODB_URI is not set in environment or Streamlit secrets")
        _client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)

    return _client[mongodb_db]
