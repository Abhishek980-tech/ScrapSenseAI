from modules.db import get_db


def ensure_indexes():
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


if __name__ == "__main__":
    ensure_indexes()
