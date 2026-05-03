import bcrypt
from datetime import datetime
from modules.db import get_db


def _users_collection():
    return get_db()["users"]


def create_user(name: str, email: str, password: str):
    users = _users_collection()

    existing = users.find_one({"email": email.lower().strip()})
    if existing:
        return False, "Email already registered."

    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    users.insert_one({
        "name": name.strip(),
        "email": email.lower().strip(),
        "password_hash": pw_hash,
        "created_at": datetime.utcnow()
    })
    return True, "Signup successful."


def verify_user(email: str, password: str):
    users = _users_collection()
    user = users.find_one({"email": email.lower().strip()})

    if not user:
        return None

    ok = bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8"))
    return user if ok else None