

import os



import os
import pandas as pd
from datetime import datetime, timezone

from .db import get_db

REPORTS_FILE = "data/reports.csv"
REPORTS_COLLECTION = os.getenv("MONGODB_REPORTS_COLLECTION", "reports")
REPORT_COLUMNS = [
    "name",
    "location_name",
    "description",
    "latitude",
    "longitude",
    "location",
    "timestamp",
    "created_at",
    "source",
    "user_email"
]


def _ensure_file_exists():
    """
    Ensure the reports CSV file and parent directory exist.
    Creates the file with headers if it does not already exist.
    """
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(REPORTS_FILE):
        df = pd.DataFrame(columns=REPORT_COLUMNS)
        df.to_csv(REPORTS_FILE, index=False)


def _normalize_report_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize report DataFrame columns to lowercase names."""
    df = df.copy()

    rename_map = {
        "Name": "name",
        "Location": "location_name",
        "Location Name": "location_name",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Description": "description",
        "Timestamp": "timestamp",
        "Created_At": "created_at",
        "createdAt": "created_at",
        "User_Email": "user_email",
        "userEmail": "user_email",
    }
    df = df.rename(columns=rename_map)

    for col in REPORT_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    return df[REPORT_COLUMNS]


def _save_report_csv(
    name: str,
    location_name: str,
    latitude: float,
    longitude: float,
    description: str,
    user_email: str = ""
) -> bool:
    """CSV fallback for save_report."""
    _ensure_file_exists()

    try:
        new_entry = pd.DataFrame([{
            "name": name.strip(),
            "location_name": location_name.strip(),
            "description": description.strip(),
            "latitude": float(latitude),
            "longitude": float(longitude),
            "location": "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "manual",
            "user_email": user_email.strip().lower()
        }])

        new_entry.to_csv(REPORTS_FILE, mode="a", header=False, index=False)
        return True
    except Exception as e:
        print(f"Error saving report to CSV: {e}")
        return False


def save_report(
    name: str,
    location_name: str,
    latitude: float,
    longitude: float,
    description: str,
    user_email: str = ""
) -> bool:
    """Save a pollution report to MongoDB when available; otherwise to CSV."""
    report_doc = {
        "name": name.strip(),
        "location_name": location_name.strip(),
        "description": description.strip(),
        "latitude": float(latitude),
        "longitude": float(longitude),
        "location": {
            "type": "Point",
            "coordinates": [float(longitude), float(latitude)]
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc),
        "source": "manual",
        "user_email": user_email.strip().lower()
    }

    try:
        reports = get_db()[REPORTS_COLLECTION]
        reports.insert_one(report_doc)
        return True
    except Exception as e:
        print(f"Error saving report to MongoDB: {e}")
        return _save_report_csv(name, location_name, latitude, longitude, description, user_email)


def _load_reports_csv() -> pd.DataFrame:
    """CSV fallback for load_reports."""
    _ensure_file_exists()

    try:
        df = pd.read_csv(REPORTS_FILE)
        return _normalize_report_df(df)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=REPORT_COLUMNS)
    except Exception as e:
        print(f"Error loading reports from CSV: {e}")
        return pd.DataFrame(columns=REPORT_COLUMNS)


def load_reports() -> pd.DataFrame:
    """Load all pollution reports from MongoDB or fallback to CSV."""
    try:
        reports = get_db()[REPORTS_COLLECTION]
        docs = list(reports.find({}, {"_id": 0}))
        if not docs:
            return pd.DataFrame(columns=REPORT_COLUMNS)

        df = pd.DataFrame(docs)
        return _normalize_report_df(df)
    except Exception as e:
        print(f"Error loading reports from MongoDB: {e}")
        return _load_reports_csv()


def get_valid_map_reports() -> pd.DataFrame:
    """Return reports with valid latitude/longitude for map rendering."""
    df = load_reports()
    if df.empty:
        return df

    df = df.dropna(subset=["latitude", "longitude"])
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    df = df[
        (df["latitude"].between(-90, 90)) &
        (df["longitude"].between(-180, 180))
    ]

    return df.reset_index(drop=True)


def save_detection_report(
    detections: list,
    location_name: str,
    latitude: float,
    longitude: float,
    user_email: str = ""
) -> bool:
    """
    Save a detection result as a report to MongoDB when available; otherwise to CSV.
    
    Args:
        detections (list): List of detection dicts with label, confidence, bbox
        location_name (str): Name of the location where detection was made
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        user_email (str): User email of who performed the detection
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    # Count detections per class
    label_counts = {}
    for d in detections:
        lbl = d["label"]
        if lbl != "Unknown Debris":
            label_counts[lbl] = label_counts.get(lbl, 0) + 1
    
    # Create summary string
    summary = ", ".join([f"{count} {cls}" for cls, count in label_counts.items()])
    if not summary:
        summary = "No debris detected"
    
    total_objects = len([d for d in detections if d["label"] != "Unknown Debris"])
    
    report_doc = {
        "name": "Detection Report",
        "location_name": location_name.strip(),
        "description": f"Detected: {summary} (Total: {total_objects} objects)",
        "latitude": float(latitude),
        "longitude": float(longitude),
        "location": {
            "type": "Point",
            "coordinates": [float(longitude), float(latitude)]
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc),
        "source": "detection",  
        "user_email": user_email.strip().lower(),
        "detections": detections  
    }

    try:
        reports = get_db()[REPORTS_COLLECTION]
        reports.insert_one(report_doc)
        return True
    except Exception as e:
        print(f"Error saving detection report to MongoDB: {e}")
        return False
