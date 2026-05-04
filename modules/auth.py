import bcrypt
<<<<<<< ours

from datetime import datetime
from .db import get_db

=======
>>>>>>> theirs
from datetime import datetime, timezone
from pymongo.errors import PyMongoError

from modules.db import get_db



def _users_collection():
    return get_db()["users"]


def create_user(name: str, email: str, password: str):
    """Create a user account. Returns (ok, message)."""
    try:
        users = _users_collection()

        existing = users.find_one({"email": email.lower().strip()})
        if existing:
            return False, "Email already registered."

        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        users.insert_one({
            "name": name.strip(),
            "email": email.lower().strip(),
            "password_hash": pw_hash,
            "created_at": datetime.now(timezone.utc)
        })
        return True, "Signup successful."
    except (ValueError, PyMongoError) as exc:
        print(f"Auth signup DB error: {exc}")
        return False, "Unable to connect to the database right now. Please try again later."


def verify_user(email: str, password: str):
    """Return user document if credentials are valid, otherwise None."""
    try:
        users = _users_collection()
        user = users.find_one({"email": email.lower().strip()})

        if not user:
            return None

        ok = bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8"))
        return user if ok else None
    except (ValueError, PyMongoError) as exc:
        print(f"Auth login DB error: {exc}")
        return None
<<<<<<< ours


    ok = bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8"))
    return user if ok else None
=======
>>>>>>> theirs
