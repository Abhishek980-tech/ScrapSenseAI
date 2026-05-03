import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "scrapsenseai")

_client = None


def get_db():
    global _client
    if _client is None:
        if not MONGODB_URI:
            raise ValueError("MONGODB_URI is not set")
        _client = MongoClient(MONGODB_URI)
    return _client[MONGODB_DB]