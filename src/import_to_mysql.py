"""Create `aicoaching` tables and load Excel sample data into MySQL."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import engine
from excel_import import data_from_excel

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "data" / "Candidate-coach sample data_v2.0.xlsx"
SCHEMA = Path(__file__).resolve().parent / "schema.sql"


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = out.where(pd.notnull(out), None)
    for col in out.columns:
        if out[col].dtype == object:
            out[col] = out[col].map(lambda v: None if v is None or str(v).strip() in {"", "nan", "NaT", "None"} else v)
    return out


def apply_schema() -> None:
    from db import db_config
    from sqlalchemy import create_engine

    cfg = db_config()
    password = cfg["password"]
    auth = cfg["user"] if not password else f"{cfg['user']}:{password}"
    root_url = f"mysql+pymysql://{auth}@{cfg['host']}:{cfg['port']}/?charset=utf8mb4"
    root = create_engine(root_url, pool_pre_ping=True)
    with root.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(
            text(
                "CREATE DATABASE IF NOT EXISTS aicoaching "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )

    sql = SCHEMA.read_text()
    statements = []
    for part in sql.split(";"):
        stmt = part.strip()
        if not stmt or stmt.startswith("--") or stmt.upper().startswith("CREATE DATABASE") or stmt.upper().startswith("USE "):
            continue
        statements.append(stmt)

    eng = engine()
    with eng.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for stmt in statements:
            conn.execute(text(stmt))


def load_raw_excel(eng) -> None:
    notes = pd.read_excel(XLSX, sheet_name="Coach Notes")
    courses = pd.read_excel(XLSX, sheet_name="Courses and events")
    meetings = pd.read_excel(XLSX, sheet_name="Coach Meeting")

    notes = notes.rename(
        columns={
            "Id": "id",
            "CandidateId": "candidate_id",
            "ProgramId": "program_id",
            "ActivityType": "activity_type",
            "ModalityType": "modality_type",
            "ActualDurationInMinutes": "actual_duration_in_minutes",
            "Notes": "notes",
            "ActivityDate": "activity_date",
            "TimelineType": "timeline_type",
        }
    )
    courses = courses.rename(
        columns={
            "CandidateId": "candidate_id",
            "CourseId": "course_id",
            "ResourceType": "resource_type",
            "EventType": "event_type",
            "EventName": "event_name",
            "EventDate": "event_date",
            "StartTime": "start_time",
            "EndTime": "end_time",
            "IsAttended": "is_attended",
            "IsRegistered": "is_registered",
            "IsSaved": "is_saved",
            "Status": "status",
            "RegisteredTimeStamp": "registered_timestamp",
            "IsClientSpecific": "is_client_specific",
        }
    )
    meetings = meetings.rename(
        columns={
            "Id": "id",
            "MeetingId": "meeting_id",
            "Title": "title",
            "MeetingEventType": "meeting_event_type",
            "Status": "status",
            "ScheduledBy": "scheduled_by",
            "ScheduledTimeStamp": "scheduled_timestamp",
            "StartTimeStamp": "start_timestamp",
            "EndTimeStamp": "end_timestamp",
            "Duration": "duration",
            "CoachEmailAddress": "coach_email_address",
            "CandidateEmailAddress": "candidate_email_address",
            "PreferredEmailAddress": "preferred_email_address",
            "CandidateId": "candidate_id",
            "CoachId": "coach_id",
            "CoachBufferTime": "coach_buffer_time",
            "CreatedTimeStamp": "created_timestamp",
            "CreatedBy": "created_by",
            "UpdatedTimeStamp": "updated_timestamp",
            "UpdatedBy": "updated_by",
        }
    )

    for col in ("activity_date",):
        notes[col] = notes[col].astype(str)
    for col in ("event_date", "start_time", "end_time", "registered_timestamp"):
        courses[col] = courses[col].astype(str)
    for col in (
        "scheduled_timestamp",
        "start_timestamp",
        "end_timestamp",
        "created_timestamp",
        "updated_timestamp",
        "preferred_email_address",
        "updated_by",
    ):
        if col in meetings.columns:
            meetings[col] = meetings[col].astype(str)

    _clean(notes).to_sql("excel_coach_notes", eng, if_exists="append", index=False)
    _clean(courses).to_sql("excel_courses_events", eng, if_exists="append", index=False)
    _clean(meetings).to_sql("excel_coach_meetings", eng, if_exists="append", index=False)


def load_app_tables(eng) -> dict[str, int]:
    data = data_from_excel(XLSX)
    order = ["coaches", "candidates", "bookings", "activities", "meeting_notes"]
    counts = {}
    for name in order:
        frame = _clean(data[name])
        frame.to_sql(name, eng, if_exists="append", index=False)
        counts[name] = len(frame)
    return counts


def main() -> None:
    apply_schema()
    eng = engine()
    app_counts = load_app_tables(eng)
    load_raw_excel(eng)
    print("Imported into aicoaching:")
    for name, n in app_counts.items():
        print(f"  {name}: {n}")
    with eng.connect() as conn:
        for table in ("excel_coach_notes", "excel_courses_events", "excel_coach_meetings"):
            n = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table}: {n}")


if __name__ == "__main__":
    main()
