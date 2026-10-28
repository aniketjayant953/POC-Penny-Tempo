"""Tempo POC - FastAPI layer.

Thin API wrapper around the existing business logic in ``src/``.
All data access goes through ``src/data_loader.load_data`` so the CSV files can
later be replaced by a database/API without touching the frontend.

Run from the project root:
    uvicorn backend.main:app --reload
"""
from __future__ import annotations

import re
import sys
from datetime import date, datetime
from pathlib import Path
from threading import Lock
from typing import Any, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# The existing modules use flat imports (``from data_loader import ...``).
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from data_loader import load_data  # noqa: E402
from candidate_prep import (  # noqa: E402
    get_upcoming_sessions,
    prepare_candidate,
    get_candidate_activities,
)
from utilization import calculate_weekly_utilization  # noqa: E402

app = FastAPI(title="Tempo POC API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Visualisation bands for 1:1 hours vs contracted AvailableHours (P3).
# Not a client SLA — most coaches sit well below 10% on this extract.
UTILIZATION_THRESHOLDS = {"high": 5.0, "moderate": 2.5}

# In-memory cache so the LLM is only called once per meeting unless refreshed.
_brief_cache: dict[str, dict[str, Any]] = {}
_brief_lock = Lock()


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _clean(value: Any) -> Any:
    """Convert pandas/numpy scalars to JSON friendly Python values."""
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        return None if pd.isna(value) else value.date().isoformat()
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        return value.item()
    return value


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [{k: _clean(v) for k, v in row.items()} for row in df.to_dict("records")]


def _today() -> pd.Timestamp:
    return pd.Timestamp(date.today())


def _candidate_row(data: dict, candidate_id: str) -> pd.Series:
    df = data["candidates"]
    match = df[df["candidate_id"] == candidate_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return match.iloc[0]


def _coach_name_map(data: dict) -> dict[str, str]:
    return dict(zip(data["coaches"]["coach_id"], data["coaches"]["coach_name"]))


def _booking_row(data: dict, booking_id: str) -> pd.Series:
    df = data["bookings"]
    match = df[df["booking_id"] == booking_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return match.iloc[0]


def _resolve_session(data: dict, candidate_id: str, booking_id: Optional[str]) -> pd.Series:
    """Find the booked session to prepare for (explicit booking, or next booked)."""
    if booking_id:
        booking = _booking_row(data, booking_id)
        if booking["candidate_id"] != candidate_id:
            raise HTTPException(status_code=400, detail="Booking does not belong to candidate.")
        return booking
    upcoming = get_upcoming_sessions(data["bookings"])
    upcoming = upcoming[upcoming["candidate_id"] == candidate_id]
    if upcoming.empty:
        raise HTTPException(status_code=404, detail="No upcoming session for this candidate.")
    return upcoming.iloc[0]


# --------------------------------------------------------------------------- #
# Basic endpoints
# --------------------------------------------------------------------------- #
@app.get("/api/health")
def health() -> dict[str, Any]:
    from db import try_load_from_db

    source = "mysql" if try_load_from_db() is not None else "excel"
    return {"status": "ok", "data_source": source, "database": "aicoaching", "today": date.today().isoformat()}


@app.get("/api/coaches")
def list_coaches(
    region: Optional[str] = None,
    has_sessions: bool = Query(False),
) -> list[dict[str, Any]]:
    data = load_data()
    df = data["coaches"].copy()
    if "region" not in df.columns:
        df["region"] = "Unknown"
    if region:
        df = df[df["region"] == region]
    if has_sessions:
        ids = set(data["bookings"]["coach_id"].astype(str))
        df = df[df["coach_id"].astype(str).isin(ids)]
    df = df.sort_values("coach_name")
    return _records(df)


@app.get("/api/candidates")
def list_candidates(coach_id: Optional[str] = None) -> list[dict[str, Any]]:
    data = load_data()
    df = data["candidates"]
    if coach_id:
        df = df[df["assigned_coach_id"] == coach_id]
    return _records(df)


@app.get("/api/candidates/{candidate_id}")
def get_candidate(candidate_id: str) -> dict[str, Any]:
    data = load_data()
    row = _candidate_row(data, candidate_id)
    names = _coach_name_map(data)
    out = {k: _clean(v) for k, v in row.to_dict().items()}
    out["assigned_coach_name"] = names.get(out["assigned_coach_id"])
    return out


# --------------------------------------------------------------------------- #
# Calendar
# --------------------------------------------------------------------------- #
@app.get("/api/bookings/upcoming")
def upcoming_bookings(coach_id: Optional[str] = None) -> dict[str, Any]:
    """Active (status = booked) sessions using the existing get_upcoming_sessions()."""
    data = load_data()
    upcoming = get_upcoming_sessions(data["bookings"])
    if coach_id:
        upcoming = upcoming[upcoming["coach_id"] == coach_id]
    today_norm = _today().normalize()
    dates = pd.to_datetime(upcoming["session_date"]).dt.normalize()
    window = upcoming[(dates >= today_norm - pd.Timedelta(weeks=4)) & (dates <= today_norm + pd.Timedelta(weeks=8))]
    if window.empty and not upcoming.empty:
        last = dates.max()
        window = upcoming[dates >= last - pd.Timedelta(weeks=8)]
    upcoming = window

    coach_names = _coach_name_map(data)
    cands = data["candidates"].set_index("candidate_id")
    today = _today()

    events = []
    for row in upcoming.to_dict("records"):
        cand = cands.loc[row["candidate_id"]]
        session_date = pd.Timestamp(row["session_date"])
        events.append(
            {
                "booking_id": row["booking_id"],
                "candidate_id": row["candidate_id"],
                "candidate_name": cand["candidate_name"],
                "coach_id": row["coach_id"],
                "coach_name": coach_names.get(row["coach_id"]),
                "session_date": session_date.date().isoformat(),
                "start_time": row["start_time"],
                "end_time": row["end_time"],
                "duration_minutes": int(row["duration_minutes"]),
                "programme": cand["programme"],
                "candidate_status": cand["status"],
                "status": row["status"],
                "is_today": bool(session_date == today),
                "is_past": bool(session_date < today),
            }
        )

    kpis = {
        # Count every booked 1:1 on the calendar, including recent past
        # meetings from the Excel sample (today may already have passed).
        "upcoming_sessions": len(events),
        "todays_sessions": sum(1 for e in events if e["is_today"]),
        "preparation_ready": len(events),
    }
    return {"today": today.date().isoformat(), "events": events, "kpis": kpis}


# --------------------------------------------------------------------------- #
# Candidate preparation
# --------------------------------------------------------------------------- #
def _split_actions(raw: Any) -> list[str]:
    if raw is None or (not isinstance(raw, str)) or not raw.strip():
        return []
    return [a.strip() for a in raw.split(";") if a.strip()]


_STATUS_RANK = ["attended", "booked", "not_attended", "cancelled"]


def _evidence_for(action: str, activities: pd.DataFrame) -> dict[str, Any]:
    """Describe what the activity data says about an action.

    Uses the same name-matching rule as check_agreed_actions() and only
    *describes* the statuses of matching activities, so we never claim a
    completion that the data does not support.
    """
    action_lower = action.lower()
    matches = [
        r
        for r in activities.to_dict("records")
        if str(r["activity_name"]).lower() in action_lower
        or action_lower in str(r["activity_name"]).lower()
    ]
    if not matches:
        return {"evidence": "not_found", "matched_activities": []}
    statuses = {str(m["status"]).lower() for m in matches}
    for s in _STATUS_RANK:
        if s in statuses:
            evidence = s
            break
    else:
        evidence = "unknown"
    return {
        "evidence": evidence,
        "matched_activities": [
            {
                "activity_id": m["activity_id"],
                "activity_name": m["activity_name"],
                "status": m["status"],
                "scheduled_date": _clean(m["scheduled_date"]),
            }
            for m in matches
        ],
    }


def _build_preparation(data: dict, candidate_id: str, session: pd.Series) -> tuple[dict, dict]:
    """Returns (raw result from prepare_candidate, API payload)."""
    candidate = _candidate_row(data, candidate_id)
    names = _coach_name_map(data)
    coach_id = session["coach_id"]
    meeting_date = pd.to_datetime(session["session_date"])

    raw = prepare_candidate(
        candidate_id=candidate_id,
        coach_id=coach_id,
        meeting_date=meeting_date,
        data=data,
    )

    all_acts = data["activities"][data["activities"]["candidate_id"] == candidate_id].copy()
    all_acts["scheduled_date"] = pd.to_datetime(all_acts["scheduled_date"])
    all_acts = all_acts.sort_values("scheduled_date")

    previous = None
    action_results: list[dict] = []
    window_activities: list[dict] = []
    if raw.get("previous_meeting_found"):
        prev_date = pd.to_datetime(raw["previous_meeting_date"])
        window_df = get_candidate_activities(data["activities"], candidate_id, prev_date, meeting_date)
        window_activities = _records(window_df)
        previous = {
            "meeting_date": prev_date.date().isoformat(),
            "notes": raw["previous_notes"],
            "agreed_actions": _split_actions(raw["agreed_actions"]),
        }
        for r in raw["action_results"]:
            item = dict(r)
            item.update(_evidence_for(r["action"], window_df))
            action_results.append(item)

    attended = int((all_acts["status"].str.lower() == "attended").sum())
    snapshot = {
        "programme": candidate["programme"],
        "status": candidate["status"],
        "assigned_coach": names.get(candidate["assigned_coach_id"]),
        "previous_meeting_date": previous["meeting_date"] if previous else None,
        "next_meeting_date": meeting_date.date().isoformat(),
        "total_activities": int(len(all_acts)),
        "attended_activities": attended,
        "window_activities": len(window_activities),
    }

    payload = {
        "candidate": {
            "candidate_id": candidate_id,
            "candidate_name": candidate["candidate_name"],
            "programme": candidate["programme"],
            "status": candidate["status"],
            "assigned_coach_id": candidate["assigned_coach_id"],
            "assigned_coach_name": names.get(candidate["assigned_coach_id"]),
        },
        "meeting": {
            "booking_id": session["booking_id"],
            "coach_id": coach_id,
            "coach_name": names.get(coach_id),
            "session_date": meeting_date.date().isoformat(),
            "start_time": session["start_time"],
            "end_time": session["end_time"],
            "duration_minutes": int(session["duration_minutes"]),
            "status": session["status"],
        },
        "previous_meeting_found": bool(raw.get("previous_meeting_found")),
        "previous_meeting": previous,
        "action_results": action_results,
        "activities": window_activities,
        "all_activities": _records(all_acts),
        "insights": raw.get("insights", []),
        "snapshot": snapshot,
    }
    return raw, payload


@app.get("/api/candidates/{candidate_id}/preparation")
def candidate_preparation(candidate_id: str, booking_id: Optional[str] = None) -> dict[str, Any]:
    data = load_data()
    session = _resolve_session(data, candidate_id, booking_id)
    _, payload = _build_preparation(data, candidate_id, session)
    return payload


# --------------------------------------------------------------------------- #
# AI brief (LLM) - only when explicitly requested
# --------------------------------------------------------------------------- #
def _parse_bullets(text: str) -> list[str]:
    bullets = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        cleaned = re.sub(r"^([-*\u2022]|\d+[.)])\s+", "", stripped)
        if cleaned != stripped:
            bullets.append(cleaned.replace("**", ""))
        elif bullets:
            bullets[-1] += " " + stripped.replace("**", "")
    return bullets or [text.strip()]


@app.post("/api/candidates/{candidate_id}/brief")
def generate_brief(
    candidate_id: str,
    booking_id: Optional[str] = None,
    refresh: bool = Query(False, description="Bypass the in-memory cache."),
) -> dict[str, Any]:
    data = load_data()
    session = _resolve_session(data, candidate_id, booking_id)
    key = f"{candidate_id}:{session['booking_id']}"

    with _brief_lock:
        if not refresh and key in _brief_cache:
            return {**_brief_cache[key], "cached": True}

        raw, _ = _build_preparation(data, candidate_id, session)
        try:
            # Imported lazily so the API still starts without LLM configuration.
            from llm_summary import generate_candidate_brief

            text = generate_candidate_brief(raw)
        except Exception as exc:  # noqa: BLE001 - never leak raw errors to the UI
            print(f"[tempo] LLM brief failed: {type(exc).__name__}: {exc}")
            raise HTTPException(
                status_code=503, detail="AI preparation is temporarily unavailable."
            ) from exc

        result = {
            "candidate_id": candidate_id,
            "booking_id": session["booking_id"],
            "bullets": _parse_bullets(text or ""),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "cached": False,
        }
        _brief_cache[key] = result
        return result


# --------------------------------------------------------------------------- #
# Utilization
# --------------------------------------------------------------------------- #
def _level(pct: float) -> str:
    if pct >= UTILIZATION_THRESHOLDS["high"]:
        return "high"
    if pct >= UTILIZATION_THRESHOLDS["moderate"]:
        return "moderate"
    return "low"


def _utilization_view(
    coach_id: Optional[str],
    start: Optional[str],
    end: Optional[str],
    region: Optional[str] = None,
) -> dict[str, Any]:
    data = load_data()
    coaches = data["coaches"].copy()
    if "region" not in coaches.columns:
        coaches["region"] = "Unknown"
    bookings = data["bookings"].copy()
    bookings["session_date"] = pd.to_datetime(bookings["session_date"]).dt.normalize()

    if region:
        coaches = coaches[coaches["region"] == region]
        bookings = bookings[bookings["coach_id"].isin(set(coaches["coach_id"]))]
    if coach_id:
        coaches = coaches[coaches["coach_id"] == coach_id]
        bookings = bookings[bookings["coach_id"] == coach_id]
    if start:
        bookings = bookings[bookings["session_date"] >= pd.to_datetime(start)]
    if end:
        end_ts = pd.to_datetime(end)
        bookings = bookings[bookings["session_date"] < end_ts + pd.Timedelta(days=7)]

    weekly = calculate_weekly_utilization(coaches, bookings)
    all_weeks = sorted(pd.to_datetime(weekly["week_start"].unique())) if not weekly.empty else []
    today = _today()
    current_week = today - pd.Timedelta(days=int(today.weekday()))

    status = bookings["status"].str.lower()
    bookings = bookings.assign(status_l=status)

    # --- weekly rows (per coach per week), straight from existing function
    weekly_rows = []
    for r in weekly.to_dict("records"):
        weekly_rows.append(
            {
                "coach_id": r["coach_id"],
                "week_start": pd.Timestamp(r["week_start"]).date().isoformat(),
                "working_hours": float(r["working_hours_per_week"]),
                "booked_hours": round(float(r["booked_coaching_hours"]), 2),
                "utilization_pct": round(float(r["utilization_percentage"]), 1),
            }
        )

    # --- weekly team trend
    trend = []
    for week, grp in weekly.groupby("week_start"):
        week_ts = pd.Timestamp(week)
        trend.append(
            {
                "week_start": week_ts.date().isoformat(),
                "avg_utilization_pct": round(float(grp["utilization_percentage"].mean()), 1),
                "booked_hours": round(float(grp["booked_coaching_hours"].sum()), 2),
                "phase": "forward" if week_ts > current_week else ("current" if week_ts == current_week else "historical"),
            }
        )

    # --- per coach table
    names = _coach_name_map(data)
    coach_rows = []
    for c in coaches.to_dict("records"):
        cid = c["coach_id"]
        wk = weekly[weekly["coach_id"] == cid]
        bk = bookings[bookings["coach_id"] == cid]
        weeks_n = int(len(wk))
        eligible_hours = float(wk["booked_coaching_hours"].sum())
        capacity = float(c["working_hours_per_week"]) * weeks_n
        pct = (eligible_hours / capacity * 100) if capacity else 0.0
        coach_rows.append(
            {
                "coach_id": cid,
                "coach_name": names.get(cid, cid),
                "region": str(c.get("region") or "Unknown"),
                "working_hours_per_week": float(c["working_hours_per_week"]),
                "weeks": weeks_n,
                "capacity_hours": round(capacity, 1),
                "eligible_hours": round(eligible_hours, 2),
                "utilization_pct": round(pct, 1),
                "level": _level(pct),
                "completed_sessions": int((bk["status_l"] == "completed").sum()),
                "booked_sessions": int((bk["status_l"] == "booked").sum()),
                "cancelled_sessions": int((bk["status_l"] == "cancelled").sum()),
            }
        )
    coach_rows.sort(key=lambda r: r["utilization_pct"], reverse=True)

    return {
        "data": data,
        "weekly_rows": weekly_rows,
        "trend": trend,
        "coach_rows": coach_rows,
        "all_weeks": [w.date().isoformat() for w in all_weeks],
        "bookings": bookings,
    }


@app.get("/api/utilization/meta")
def utilization_meta() -> dict[str, Any]:
    data = load_data()
    coaches = data["coaches"].copy()
    if "region" not in coaches.columns:
        coaches["region"] = "Unknown"
    bookings = data["bookings"].copy()
    bookings["session_date"] = pd.to_datetime(bookings["session_date"]).dt.normalize()
    week = (
        bookings["session_date"] - pd.to_timedelta(bookings["session_date"].dt.weekday, unit="D")
    ).dt.normalize()
    weeks = sorted({pd.Timestamp(w).date().isoformat() for w in week if not pd.isna(w)})
    regions = sorted({str(r) for r in coaches["region"].dropna().unique() if str(r).strip()})

    today = _today().normalize()
    current_week = today - pd.Timedelta(days=int(today.weekday()))
    default_end = current_week
    default_start = current_week - pd.Timedelta(weeks=11)
    if weeks:
        last = pd.Timestamp(weeks[-1])
        first = pd.Timestamp(weeks[0])
        if default_end > last or default_start > last:
            default_end = last
            default_start = last - pd.Timedelta(weeks=11)
        if default_start < first:
            default_start = first

    default_region = (
        "United Kingdom & Ireland" if "United Kingdom & Ireland" in regions else (regions[0] if regions else "")
    )
    return {
        "weeks": weeks,
        "regions": regions,
        "default_start": default_start.date().isoformat(),
        "default_end": default_end.date().isoformat(),
        "default_region": default_region,
        "thresholds": UTILIZATION_THRESHOLDS,
        "source": "P3 Coach_RelatedDetails",
    }


@app.get("/api/utilization")
def utilization(
    coach_id: Optional[str] = None,
    start: Optional[str] = Query(None, description="Week start (YYYY-MM-DD), inclusive"),
    end: Optional[str] = Query(None, description="Week start (YYYY-MM-DD), inclusive"),
    region: Optional[str] = None,
) -> dict[str, Any]:
    view = _utilization_view(coach_id, start, end, region)
    return {
        "weeks": view["all_weeks"],
        "thresholds": UTILIZATION_THRESHOLDS,
        "coaches": view["coach_rows"],
        "trend": view["trend"],
        "weekly": view["weekly_rows"],
    }


@app.get("/api/utilization/summary")
def utilization_summary(
    coach_id: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    region: Optional[str] = None,
) -> dict[str, Any]:
    view = _utilization_view(coach_id, start, end, region)
    rows = view["coach_rows"]
    bookings = view["bookings"]

    if not rows or not view["trend"]:
        return {"has_data": False, "kpis": None, "insights": []}

    total_hours = sum(r["eligible_hours"] for r in rows)
    total_capacity = sum(r["capacity_hours"] for r in rows)
    avg_util = (total_hours / total_capacity * 100) if total_capacity else 0.0
    cancelled = int((bookings["status_l"] == "cancelled").sum())
    total_sessions = int(len(bookings))
    highest = max(rows, key=lambda r: r["utilization_pct"])
    lowest = min(rows, key=lambda r: r["utilization_pct"])

    kpis = {
        "total_coaches": len(rows),
        "average_utilization_pct": round(avg_util, 1),
        "total_coaching_hours": round(total_hours, 1),
        "cancelled_sessions": cancelled,
        "highest": {"coach_name": highest["coach_name"], "utilization_pct": highest["utilization_pct"]},
        "lowest": {"coach_name": lowest["coach_name"], "utilization_pct": lowest["utilization_pct"]},
    }

    insights: list[dict[str, str]] = []
    if len(rows) > 1:
        insights.append({"kind": "positive", "title": "Highest utilization",
                         "text": f"{highest['coach_name']} has the highest utilization at {highest['utilization_pct']:.1f}%."})
        insights.append({"kind": "attention", "title": "Lowest utilization",
                         "text": f"{lowest['coach_name']} has the lowest utilization at {lowest['utilization_pct']:.1f}%."})
    insights.append({"kind": "neutral", "title": "Team average",
                     "text": f"Average team utilization is {avg_util:.1f}% across {len(rows)} coach{'es' if len(rows) != 1 else ''}."})
    if total_sessions:
        insights.append({"kind": "attention" if cancelled else "neutral", "title": "Cancellations",
                         "text": f"{cancelled} of {total_sessions} sessions ({cancelled / total_sessions * 100:.1f}%) were cancelled."})
    most_cancel = max(rows, key=lambda r: r["cancelled_sessions"])
    if len(rows) > 1 and most_cancel["cancelled_sessions"] > 0:
        insights.append({"kind": "attention", "title": "Most cancellations",
                         "text": f"{most_cancel['coach_name']} had the most cancelled sessions ({most_cancel['cancelled_sessions']})."})
    insights.append({"kind": "neutral", "title": "Capacity headroom",
                     "text": f"{total_hours:.1f} eligible session hours were used out of {total_capacity:,.0f} working hours of capacity."})
    if len(rows) > 1:
        below = sum(1 for r in rows if r["utilization_pct"] < avg_util)
        insights.append({"kind": "neutral", "title": "Below team average",
                         "text": f"{below} of {len(rows)} coaches are below the team average of {avg_util:.1f}%."})
    peak = max(view["trend"], key=lambda t: t["avg_utilization_pct"])
    if len(view["trend"]) > 1:
        insights.append({"kind": "neutral", "title": "Peak week",
                         "text": f"Week of {peak['week_start']} had the highest average utilization at {peak['avg_utilization_pct']:.1f}%."})

    return {"has_data": True, "kpis": kpis, "insights": insights}
