from pathlib import Path
from typing import Optional

import pandas as pd

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directory
DATA_DIR = BASE_DIR / "data"
P3_PATH = DATA_DIR / "Coach_RelatedDetails_P3.xlsx"
EXCEL_PATH = DATA_DIR / "Candidate-coach sample data_v2.0.xlsx"

_CACHE: Optional[dict] = None


def load_data(refresh: bool = False):
    """Load all Tempo POC datasets.

    Prefers MySQL (`aicoaching`) when tables are populated, then the P3
    workbook, then the older sample workbook, then CSV files.
    """
    global _CACHE
    if _CACHE is not None and not refresh:
        return _CACHE

    from db import try_load_from_db

    db_data = try_load_from_db()
    if db_data is not None:
        _CACHE = db_data
        return db_data

    if P3_PATH.exists():
        from p3_import import data_from_p3

        _CACHE = data_from_p3(P3_PATH)
        return _CACHE

    if EXCEL_PATH.exists():
        from excel_import import data_from_excel

        _CACHE = data_from_excel(EXCEL_PATH)
        return _CACHE

    coaches = pd.read_csv(DATA_DIR/"coaches.csv")
    candidates = pd.read_csv(DATA_DIR/"candidates.csv")
    bookings = pd.read_csv(DATA_DIR/"coach_bookings.csv")
    activities = pd.read_csv(DATA_DIR/"candidate_activities.csv") 
    meeting_notes = pd.read_csv(DATA_DIR/"previous_coach_meeting_notes.csv") 

    _CACHE = {
        "coaches": coaches,
        "candidates": candidates,
        "bookings": bookings,
        "activities": activities,
        "meeting_notes": meeting_notes,
    }
    return _CACHE

def validate_data(data):
    """Perform basic validation on the data""" 

    coaches = data["coaches"]
    candidates = data["candidates"] 
    bookings = data["bookings"]
    activities = data["activities"]
    meeting_notes = data["meeting_notes"]

    # validate coach IDs 

    valid_coach_ids = set(coaches["coach_id"])  

    invalid_booking_coaches = set(bookings["coach_id"]) - valid_coach_ids  

    if invalid_booking_coaches:
        raise ValueError(f"Invalid coach IDs in bookings: {invalid_booking_coaches}") 

    # Validate candidate IDs
    valid_candidate_ids = set(candidates["candidate_id"])

    invalid_booking_candidates = set(bookings["candidate_id"]) - valid_candidate_ids
    
    if invalid_booking_candidates: 
        raise ValueError(f"Invalid candidate IDs in bookings: {invalid_booking_candidates}")

    invalid_activity_candidates = set(activities["candidate_id"]) - valid_candidate_ids

    if invalid_activity_candidates:
        raise ValueError(f"Invlaid candidate IDs in activities: {invalid_activity_candidates}")

    invalid_meeting_note_candidates = set(meeting_notes["candidate_id"]) - valid_candidate_ids

    if invalid_meeting_note_candidates:
        raise ValueError(f"Invalid candidate IDs in meeting notes: {invalid_meeting_note_candidates}")

    print("Data validation passed successfully")

if __name__ == "__main__":
    data = load_data()

    validate_data(data)

    for name, dataframe in data.items():
        print(f"{name}: {len(dataframe)} rows")



