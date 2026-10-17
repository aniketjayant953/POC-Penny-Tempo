"""Map the Candidate-coach Excel workbook onto the Tempo POC dataframes."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

# Sample workbook uses two candidate GUIDs that differ by one character
# (notes vs meetings/courses). Treat them as the same person.
CANDIDATE_ALIASES = {
    "A7C1787A-7EF8-4CCA-3EC9-08DED5E6B6F5": "E7C1787E-7EF8-4CCA-3EC9-08DED5E6B6F5",
}

SENTINEL_PREFIX = "0001-01-01"


def _norm_id(value: object) -> str:
    text = str(value).strip()
    return CANDIDATE_ALIASES.get(text.upper(), text) if text else ""


_TITLE_LABELS = {
    "careeroptionsandplanning": "Career Options and Planning",
    "interviewpreparation": "Interview Preparation",
    "linkedinprofile": "LinkedIn Profile",
    "cvandapplications": "CV and Applications",
}


def _humanize(value: object) -> str:
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return ""
    last = text.split(".")[-1]
    mapped = _TITLE_LABELS.get(last.lower())
    if mapped:
        return mapped
    last = re.sub(r"([a-z])([A-Z])", r"\1 \2", last)
    last = last.replace("_", " ").replace("-", " ")
    return " ".join(last.split()).title()


def _parse_dt(value: object) -> pd.Timestamp:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return pd.NaT
    if isinstance(value, pd.Timestamp):
        ts = value.tz_localize(None) if value.tzinfo else value
        return pd.NaT if ts.year <= 1 else ts
    text = str(value).strip()
    if not text or text.lower() == "nan" or text.startswith(SENTINEL_PREFIX):
        return pd.NaT
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2}))?", text)
    if match:
        year, first, second = int(match.group(1)), int(match.group(2)), int(match.group(3))
        hour = int(match.group(4) or 0)
        minute = int(match.group(5) or 0)
        month, day = first, second
        if first > 12 and second <= 12:
            day, month = first, second
        try:
            return pd.Timestamp(year=year, month=month, day=day, hour=hour, minute=minute)
        except ValueError:
            return pd.NaT
    parsed = pd.to_datetime(text, utc=True, errors="coerce")
    if pd.isna(parsed):
        return pd.NaT
    parsed = parsed.tz_localize(None)
    return pd.NaT if parsed.year <= 1 else parsed


def _hhmm(value: pd.Timestamp) -> str:
    if pd.isna(value):
        return ""
    return pd.Timestamp(value).strftime("%H:%M")


def _iso_date(value: pd.Timestamp) -> str:
    if pd.isna(value):
        return ""
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def _name_from_notes(notes: pd.Series) -> str:
    for text in notes.dropna().astype(str):
        match = re.search(r"\b(?:with|Caught up with)\s+([A-Z][a-z]+)\b", text)
        if match:
            return match.group(1)
        match = re.search(r"\b([A-Z][a-z]+)\s+is struggling\b", text)
        if match:
            return match.group(1)
    return ""


def _name_from_email(email: object) -> str:
    text = str(email or "").strip()
    if not text or "@" not in text:
        return ""
    local = text.split("@")[0]
    parts = [p for p in re.split(r"[._-]+", local) if p]
    if len(parts) >= 2:
        return " ".join(p.capitalize() for p in parts)
    return text


def _activity_status(row: pd.Series) -> str:
    if int(row.get("IsAttended") or 0) == 1:
        return "attended"
    status = str(row.get("Status") or "").strip().lower()
    if status == "non_subscribed":
        return "cancelled"
    if int(row.get("IsRegistered") or 0) == 1:
        return "booked"
    return "cancelled"


def data_from_excel(path: Path) -> dict[str, pd.DataFrame]:
    sheets = pd.read_excel(path, sheet_name=["Coach Notes", "Courses and events", "Coach Meeting"])
    notes_raw = sheets["Coach Notes"]
    courses_raw = sheets["Courses and events"]
    meetings_raw = sheets["Coach Meeting"]

    meetings = meetings_raw.copy()
    meetings["CandidateId"] = meetings["CandidateId"].map(_norm_id)
    meetings["start"] = meetings["StartTimeStamp"].map(_parse_dt)
    meetings["end"] = meetings["EndTimeStamp"].map(_parse_dt)
    meetings["created"] = meetings["CreatedTimeStamp"].map(_parse_dt)
    meetings = meetings.dropna(subset=["start"])

    if meetings.empty:
        raise ValueError(f"No valid coach meetings found in {path.name}")

    notes_raw = notes_raw.copy()
    notes_raw["CandidateId"] = notes_raw["CandidateId"].map(_norm_id)

    coach_rows = []
    seen_coaches: set[str] = set()
    for row in meetings.to_dict("records"):
        coach_id = str(row.get("CoachId") or "").strip()
        if not coach_id or coach_id in seen_coaches:
            continue
        seen_coaches.add(coach_id)
        email = str(row.get("CoachEmailAddress") or "").strip()
        coach_rows.append(
            {
                "coach_id": coach_id,
                "coach_name": _name_from_email(email) or email or "Coach",
                "working_hours_per_week": 37,
                "working_days": "Mon;Tue;Wed;Thu;Fri",
                "timezone": "Europe/London",
            }
        )
    coaches = pd.DataFrame(coach_rows)

    notes_by_candidate: dict[str, list[str]] = {}
    for row in notes_raw.to_dict("records"):
        cid = _norm_id(row.get("CandidateId"))
        if cid:
            notes_by_candidate.setdefault(cid, []).append(str(row.get("Notes") or ""))

    latest_meeting = (
        meetings.sort_values("start")
        .groupby("CandidateId", as_index=False)
        .tail(1)
        .set_index("CandidateId")
    )

    candidate_rows = []
    seen_candidates: set[str] = set()
    for row in meetings.to_dict("records"):
        candidate_id = str(row.get("CandidateId") or "").strip()
        if not candidate_id or candidate_id in seen_candidates:
            continue
        seen_candidates.add(candidate_id)
        email = str(row.get("CandidateEmailAddress") or "").strip()
        latest = latest_meeting.loc[candidate_id] if candidate_id in latest_meeting.index else row
        if isinstance(latest, pd.DataFrame):
            latest = latest.iloc[-1]
        programme = _humanize(latest.get("Title")) or "Career Options and Planning"
        note_name = _name_from_notes(pd.Series(notes_by_candidate.get(candidate_id, [])))
        candidate_rows.append(
            {
                "candidate_id": candidate_id,
                "candidate_name": note_name or _name_from_email(email) or "Candidate",
                "programme": programme,
                "status": "Active",
                "assigned_coach_id": str(row.get("CoachId") or "").strip(),
            }
        )
    candidates = pd.DataFrame(candidate_rows)

    booking_rows = []
    for row in meetings.to_dict("records"):
        start, end = row["start"], row["end"]
        duration = int(row.get("Duration") or 0)
        if duration <= 0 and not pd.isna(start) and not pd.isna(end):
            duration = int((end - start).total_seconds() // 60)
        excel_status = str(row.get("Status") or "").strip().lower()
        if excel_status in {"cancelled", "canceled", "declined"}:
            status = "cancelled"
        elif excel_status in {"completed", "finished"}:
            status = "completed"
        else:
            status = "booked"
        booking_rows.append(
            {
                "booking_id": str(row.get("MeetingId") or row.get("Id")).strip(),
                "coach_id": str(row["CoachId"]).strip(),
                "candidate_id": str(row["CandidateId"]).strip(),
                "session_date": _iso_date(start),
                "start_time": _hhmm(start) or "09:00",
                "end_time": _hhmm(end) or _hhmm(start + pd.Timedelta(minutes=duration or 45)),
                "duration_minutes": duration or 45,
                "status": status,
                "created_date": _iso_date(row["created"]) or _iso_date(start),
            }
        )
    bookings = pd.DataFrame(booking_rows)

    note_rows = []
    coach_by_candidate = dict(zip(candidates["candidate_id"], candidates["assigned_coach_id"]))
    bookings_by_key = {
        (r["candidate_id"], r["session_date"]): r["booking_id"]
        for r in booking_rows
        if r.get("session_date")
    }
    for row in notes_raw.to_dict("records"):
        when = _parse_dt(row.get("ActivityDate"))
        if pd.isna(when):
            continue
        date_key = _iso_date(when)
        candidate_id = _norm_id(row.get("CandidateId"))
        note_rows.append(
            {
                "meeting_id": str(row.get("Id")).strip(),
                "coach_id": coach_by_candidate.get(candidate_id, ""),
                "candidate_id": candidate_id,
                "meeting_date": date_key,
                "booking_id": bookings_by_key.get((candidate_id, date_key), ""),
                "notes": str(row.get("Notes") or "").strip(),
                "agreed_actions": "",
            }
        )
    meeting_notes = pd.DataFrame(note_rows)

    activity_rows = []
    for idx, row in courses_raw.iterrows():
        candidate_id = _norm_id(row.get("CandidateId"))
        if not candidate_id:
            continue
        scheduled = _parse_dt(row.get("EventDate"))
        if pd.isna(scheduled):
            scheduled = _parse_dt(row.get("StartTime"))
        if pd.isna(scheduled):
            continue
        start = _parse_dt(row.get("StartTime"))
        end = _parse_dt(row.get("EndTime"))
        duration = 0
        if not pd.isna(start) and not pd.isna(end):
            duration = int((end - start).total_seconds() // 60)
        event_type = str(row.get("EventType") or "").strip()
        activity_type = "on_demand" if event_type.lower() == "ondemand" else "live"
        status = _activity_status(row)
        attended = status == "attended"
        activity_rows.append(
            {
                "activity_id": f"ACT{idx + 1:04d}",
                "candidate_id": _norm_id(row.get("CandidateId")),
                "activity_name": str(row.get("EventName") or "").strip(),
                "activity_type": activity_type,
                "scheduled_date": _iso_date(scheduled),
                "completion_date": _iso_date(scheduled) if attended else "",
                "status": status,
                "duration_minutes": duration or 60,
            }
        )
    activities = pd.DataFrame(activity_rows)

    return {
        "coaches": coaches,
        "candidates": candidates,
        "bookings": bookings,
        "activities": activities,
        "meeting_notes": meeting_notes,
    }


def write_csv_bundle(data: dict[str, pd.DataFrame], data_dir: Path) -> None:
    mapping = {
        "coaches": "coaches.csv",
        "candidates": "candidates.csv",
        "bookings": "coach_bookings.csv",
        "activities": "candidate_activities.csv",
        "meeting_notes": "previous_coach_meeting_notes.csv",
    }
    data_dir.mkdir(parents=True, exist_ok=True)
    for key, filename in mapping.items():
        data[key].to_csv(data_dir / filename, index=False)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    xlsx = root / "data" / "Candidate-coach sample data_v2.0.xlsx"
    bundle = data_from_excel(xlsx)
    write_csv_bundle(bundle, root / "data")
    for name, frame in bundle.items():
        print(f"{name}: {len(frame)} rows")
