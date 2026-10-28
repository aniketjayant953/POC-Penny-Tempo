"""Create `aicoaching` tables and load P3 coach utilisation data into MySQL.

Replaces any previous dummy / sample-workbook rows.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import engine
from p3_import import data_from_p3

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "data" / "Coach_RelatedDetails_P3.xlsx"
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


def load_app_tables(eng) -> dict[str, int]:
    data = data_from_p3(XLSX)
    order = ["coaches", "candidates", "bookings", "activities", "meeting_notes"]
    counts = {}
    for name in order:
        frame = _clean(data[name])
        if frame.empty:
            counts[name] = 0
            continue
        frame.to_sql(name, eng, if_exists="append", index=False, chunksize=2000, method="multi")
        counts[name] = len(frame)
    return counts


def main() -> None:
    if not XLSX.exists():
        raise FileNotFoundError(f"Missing {XLSX}")
    apply_schema()
    eng = engine()
    app_counts = load_app_tables(eng)
    print("Imported P3 data into aicoaching (dummy rows dropped):")
    for name, n in app_counts.items():
        print(f"  {name}: {n}")


if __name__ == "__main__":
    main()
