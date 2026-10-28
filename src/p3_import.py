"""Map Coach_RelatedDetails_P3.xlsx onto Tempo coaches / bookings tables."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

PLACEHOLDER_CANDIDATE_ID = "P3-NO-CANDIDATE"
DEFAULT_WORKING_HOURS = 37.0

_TZ_BY_REGION = {
    "australia": "Australia/Sydney",
    "japan": "Asia/Tokyo",
    "singapore": "Asia/Singapore",
    "asean-k": "Asia/Singapore",
    "asia pacific": "Asia/Singapore",
    "united arab emirates": "Asia/Dubai",
    "united kingdom & ireland": "Europe/London",
    "nordic": "Europe/Stockholm",
    "nordic - manpower": "Europe/Stockholm",
    "central europe": "Europe/Berlin",
    "central europe - manpower": "Europe/Berlin",
    "france - mediterranean": "Europe/Paris",
    "southern emea - manpower": "Europe/Madrid",
    "north america region": "America/New_York",
    "americas latin america": "America/Sao_Paulo",
    "affiliate - florida/caribbean": "America/New_York",
    "affiliate - great lakes": "America/Chicago",
}


def _norm_id(value: object) -> str:
    return str(value or "").strip().upper()


def _display_name(value: object, coach_id: str) -> str:
    text = str(value or "").strip()
    if not text or text.lower() in {"nan", "none"}:
        return f"Coach {coach_id[:8]}"
    if "," in text:
        last, first = [p.strip() for p in text.split(",", 1)]
        if first and last:
            return f"{first} {last}"
    return text


def _parse_dt(value: object) -> pd.Timestamp:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return pd.NaT
    if isinstance(value, pd.Timestamp):
        ts = value.tz_localize(None) if value.tzinfo else value
        return pd.NaT if ts.year <= 1 else ts
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return pd.NaT
    text = re.sub(r"\.\d+", "", text)
    text = text.replace(" +00:00", "").replace("+00:00", "").strip()
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        return pd.NaT
    if getattr(parsed, "tzinfo", None):
        parsed = parsed.tz_localize(None)
    return parsed


def _hhmm(value: pd.Timestamp) -> str:
    if pd.isna(value):
        return "09:00"
    return pd.Timestamp(value).strftime("%H:%M")


def _iso_date(value: pd.Timestamp) -> str:
    if pd.isna(value):
        return ""
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def _timezone(region: str) -> str:
    return _TZ_BY_REGION.get((region or "").strip().lower(), "Europe/London")


def data_from_p3(path: Path) -> dict[str, pd.DataFrame]:
    coaches_raw = pd.read_excel(path, sheet_name="CoachSummary")
    sessions_raw = pd.read_excel(path, sheet_name="SessionSummary")
    avail_raw = pd.read_excel(path, sheet_name="CoachAvailability")

    avail = {
        _norm_id(r["CoachID"]): float(r["AvailableHours"])
        for r in avail_raw.to_dict("records")
        if _norm_id(r.get("CoachID"))
    }
    region_by_id: dict[str, str] = {}
    name_by_id: dict[str, str] = {}
    for r in coaches_raw.to_dict("records"):
        cid = _norm_id(r.get("CoachID"))
        if not cid:
            continue
        region_by_id[cid] = str(r.get("Region") or "").strip() or "Unknown"
        name_by_id[cid] = _display_name(r.get("CoachName"), cid)

    extra_ids = {_norm_id(r.get("CoachID")) for r in sessions_raw.to_dict("records")}
    extra_ids |= set(avail)
    extra_ids.discard("")

    coach_rows = []
    seen: set[str] = set()
    for cid in list(name_by_id) + sorted(extra_ids):
        if not cid or cid in seen:
            continue
        seen.add(cid)
        region = region_by_id.get(cid, "Unknown")
        coach_rows.append(
            {
                "coach_id": cid,
                "coach_name": name_by_id.get(cid) or f"Coach {cid[:8]}",
                "region": region,
                "working_hours_per_week": float(avail.get(cid, DEFAULT_WORKING_HOURS)),
                "working_days": "Mon;Tue;Wed;Thu;Fri",
                "timezone": _timezone(region),
            }
        )
    coaches = pd.DataFrame(coach_rows)
    if coaches.empty:
        raise ValueError(f"No coaches found in {path.name}")

    placeholder_coach = coaches.iloc[0]["coach_id"]
    candidates = pd.DataFrame(
        [
            {
                "candidate_id": PLACEHOLDER_CANDIDATE_ID,
                "candidate_name": "Candidate (not in P3 extract)",
                "programme": "Coaching 1:1",
                "status": "Unknown",
                "assigned_coach_id": placeholder_coach,
            }
        ]
    )

    booking_rows = []
    seen_bookings: set[str] = set()
    valid_coaches = set(coaches["coach_id"])
    for r in sessions_raw.to_dict("records"):
        booking_id = str(r.get("SessionID") or "").strip()
        coach_id = _norm_id(r.get("CoachID"))
        start = _parse_dt(r.get("SessionDate"))
        if not booking_id or booking_id in seen_bookings or not coach_id or pd.isna(start):
            continue
        if coach_id not in valid_coaches:
            continue
        seen_bookings.add(booking_id)
        hours = float(r.get("Hours") or 0)
        duration = int(round(hours * 60)) if hours > 0 else 0
        end = start + pd.Timedelta(minutes=duration or 30)
        status_raw = str(r.get("status") or "").strip().lower()
        if status_raw in {"cancelled", "canceled", "declined"}:
            status = "cancelled"
        elif status_raw in {"completed", "finished"}:
            status = "completed"
        else:
            # P3 extract uses Accepted — eligible for utilisation (booked + completed).
            status = "booked"
        booking_rows.append(
            {
                "booking_id": booking_id[:64],
                "coach_id": coach_id,
                "candidate_id": PLACEHOLDER_CANDIDATE_ID,
                "session_date": _iso_date(start),
                "start_time": _hhmm(start),
                "end_time": _hhmm(end),
                "duration_minutes": duration,
                "status": status,
                "created_date": _iso_date(start),
            }
        )
    bookings = pd.DataFrame(booking_rows)
    if bookings.empty:
        raise ValueError(f"No sessions found in {path.name}")

    activities = pd.DataFrame(
        columns=[
            "activity_id",
            "candidate_id",
            "activity_name",
            "activity_type",
            "scheduled_date",
            "completion_date",
            "status",
            "duration_minutes",
        ]
    )
    meeting_notes = pd.DataFrame(
        columns=[
            "meeting_id",
            "coach_id",
            "candidate_id",
            "meeting_date",
            "booking_id",
            "notes",
            "agreed_actions",
        ]
    )

    return {
        "coaches": coaches,
        "candidates": candidates,
        "bookings": bookings,
        "activities": activities,
        "meeting_notes": meeting_notes,
    }
