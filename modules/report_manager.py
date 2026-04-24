"""
report_manager.py
-----------------
Handles saving and loading community pollution reports to/from a CSV file.
"""

import os
import pandas as pd
from datetime import datetime


REPORTS_FILE = "data/reports.csv"
COLUMNS = ["Name", "Location", "Latitude", "Longitude", "Description", "Timestamp"]


def _ensure_file_exists():
    """
    Ensure the reports CSV file and parent directory exist.
    Creates the file with headers if it does not already exist.
    """
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(REPORTS_FILE):
        # Create an empty DataFrame with the correct columns and save it
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(REPORTS_FILE, index=False)


def save_report(name: str, location: str, latitude: float, longitude: float, description: str) -> bool:
    """
    Append a new pollution report to the CSV file.

    Args:
        name (str): Reporter's name.
        location (str): Location name/description.
        latitude (float): GPS latitude coordinate.
        longitude (float): GPS longitude coordinate.
        description (str): Description of the pollution observed.

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    _ensure_file_exists()

    try:
        new_entry = pd.DataFrame([{
            "Name": name.strip(),
            "Location": location.strip(),
            "Latitude": latitude,
            "Longitude": longitude,
            "Description": description.strip(),
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])

        # Append without writing headers again
        new_entry.to_csv(REPORTS_FILE, mode="a", header=False, index=False)
        return True

    except Exception as e:
        print(f"Error saving report: {e}")
        return False


def load_reports() -> pd.DataFrame:
    """
    Load all pollution reports from the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing all reports, or empty DataFrame if file is missing.
    """
    _ensure_file_exists()

    try:
        df = pd.read_csv(REPORTS_FILE)

        # Ensure all expected columns exist (handle partially written files)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""

        return df

    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=COLUMNS)

    except Exception as e:
        print(f"Error loading reports: {e}")
        return pd.DataFrame(columns=COLUMNS)


def get_valid_map_reports() -> pd.DataFrame:
    """
    Return reports that have valid (non-null, in-range) latitude/longitude values.
    Used for rendering markers on the pollution map.

    Returns:
        pd.DataFrame: Filtered DataFrame with valid GPS coordinates.
    """
    df = load_reports()

    if df.empty:
        return df

    # Drop rows with missing coordinates
    df = df.dropna(subset=["Latitude", "Longitude"])

    # Convert to numeric, coercing errors
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

    # Filter to valid geographic ranges
    df = df[
        (df["Latitude"].between(-90, 90)) &
        (df["Longitude"].between(-180, 180))
    ]

    return df.reset_index(drop=True)
