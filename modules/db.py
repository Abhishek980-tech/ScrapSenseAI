import os
from pymongo import MongoClient, errors
import ssl
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
    mongodb_db = _get_env_value("MONGODB_DB", "scrapsenseai")
    if _client is None:
        mongodb_uri = _get_env_value("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError(
                "MONGODB_URI is not set. "
                "Set it in a local .env file or configure it in your deployment environment / Streamlit secrets."
            )
        if "your-mongodb-connection-string" in mongodb_uri:
            raise ValueError(
                "MONGODB_URI is still using the placeholder string. "
                "Replace it with your actual MongoDB connection string in .env or Streamlit Secrets."
            )
        try:
            _client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                tls=True,
                tlsAllowInvalidCertificates=False,
                tlsAllowInvalidHostnames=False,
                ssl_version=ssl.PROTOCOL_TLSv1_2,
            )
            _client.admin.command("ping")
        except errors.PyMongoError as exc:
            raise ConnectionError(
                "Unable to reach MongoDB. "
                "Verify your MONGODB_URI / Streamlit secrets and ensure the MongoDB cluster allows connections from the deployment environment."
            ) from exc
    return _client[mongodb_db]


def check_db_connection():
    """Validate MongoDB connectivity before authentication flows."""
    try:
        get_db()
    except Exception as exc:
        raise ConnectionError(str(exc)) from exc
