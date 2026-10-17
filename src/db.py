"""MySQL connection for the Tempo POC (XAMPP phpMyAdmin database `aicoaching`)."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

load_dotenv(Path(__file__).resolve().parent / ".env")

TABLES = {
    "coaches": "coaches",
    "candidates": "candidates",
    "bookings": "bookings",
    "activities": "activities",
    "meeting_notes": "meeting_notes",
}


def db_config() -> dict[str, str]:
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": os.getenv("DB_PORT", "3306"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "name": os.getenv("DB_NAME", "aicoaching"),
    }


def engine() -> Engine:
    cfg = db_config()
    password = cfg["password"]
    auth = cfg["user"] if not password else f"{cfg['user']}:{password}"
    url = f"mysql+pymysql://{auth}@{cfg['host']}:{cfg['port']}/{cfg['name']}?charset=utf8mb4"
    return create_engine(url, pool_pre_ping=True)


def try_load_from_db() -> dict[str, pd.DataFrame] | None:
    """Return app datasets from MySQL, or None if the DB is empty/unavailable."""
    try:
        eng = engine()
        with eng.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM coaches")).scalar()
        if not count:
            return None
        return {key: pd.read_sql_table(table, eng) for key, table in TABLES.items()}
    except Exception:
        return None
