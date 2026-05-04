<<<<<<< ours

from .db import get_db

from modules.db import get_db


import sys
from pymongo.errors import PyMongoError


from modules.db import get_db

=======
import sys
from pymongo.errors import PyMongoError

from modules.db import get_db

>>>>>>> theirs

def ensure_indexes() -> bool:
    """Create required MongoDB indexes. Returns True on success."""
    try:
        db = get_db()
        db.users.create_index("email", unique=True)
        db.reports.create_index([("created_at", -1)])
        db.reports.create_index([("location", "2dsphere")])
        db.reports.create_index([("latitude", 1), ("longitude", 1)])

        print("MongoDB indexes created:")
        print("  - users.email (unique)")
        print("  - reports.created_at (-1)")
        print("  - reports.location (2dsphere)")
        print("  - reports.latitude + reports.longitude")
        return True
    except ValueError as exc:
        print(f"MongoDB setup failed: {exc}")
        print("Set MONGODB_URI in your .env before running index setup.")
        return False
    except PyMongoError as exc:
        print("MongoDB setup failed: unable to connect or authenticate.")
        print(f"Details: {exc}")
        print("Troubleshooting:")
        print("  1) Verify MONGODB_URI, username, and password in .env")
        print("  2) Ensure your current IP is allowed in MongoDB Atlas Network Access")
        print("  3) Check local TLS/SSL support and system clock correctness")
        return False


if __name__ == "__main__":
    ok = ensure_indexes()
    sys.exit(0 if ok else 1)
