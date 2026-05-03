import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_env_value(key: str, default=None):
    value = os.getenv(key)
    if value:
        return value

    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default


def get_db():
    global _client
    if _client is None:
        mongodb_uri = _get_env_value("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError(
                "MONGODB_URI is not set. "
                "Set it in a local .env file or configure it in your deployment environment / Streamlit secrets."
            )

        mongodb_db = _get_env_value("MONGODB_DB", "scrapsenseai")
        _client = MongoClient(mongodb_uri)
    return _client[mongodb_db]