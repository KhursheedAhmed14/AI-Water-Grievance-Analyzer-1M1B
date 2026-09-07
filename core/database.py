import os
import sqlite3
from datetime import datetime
from pathlib import Path
import streamlit as st

# Resolve DB path relative to the project root, regardless of CWD
DB_PATH = Path(__file__).parent.parent / "data" / "grievances.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS complaints (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    submitted_at     TEXT,
    raw_text         TEXT,
    summary          TEXT,
    category         TEXT,
    severity         TEXT,
    priority         TEXT,
    location         TEXT,
    duration         TEXT,
    affected_people  TEXT,
    missing_info     TEXT,
    key_facts        TEXT,
    raw_llm_response TEXT
)
"""


def _get_connection() -> sqlite3.Connection:
    """Return a sqlite3 connection with row_factory set to sqlite3.Row."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the data/ directory and complaints table if they do not exist."""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = _get_connection()
    try:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()
    finally:
        conn.close()


def insert_complaint(record: dict) -> int:
    """
    Persist a fully-analyzed complaint record and return its new row ID.
    Clear cached complaints list to reflect the new record immediately.
    """
    row = {
        "submitted_at":     record.get("submitted_at", datetime.utcnow().isoformat()),
        "raw_text":         record.get("raw_text"),
        "summary":          record.get("summary"),
        "category":         record.get("category"),
        "severity":         record.get("severity"),
        "priority":         record.get("priority"),
        "location":         record.get("location"),
        "duration":         record.get("duration"),
        "affected_people":  record.get("affected_people"),
        "missing_info":     record.get("missing_info"),
        "key_facts":        record.get("key_facts"),
        "raw_llm_response": record.get("raw_llm_response"),
    }
    sql = """
        INSERT INTO complaints
            (submitted_at, raw_text, summary, category, severity, priority,
             location, duration, affected_people, missing_info, key_facts,
             raw_llm_response)
        VALUES
            (:submitted_at, :raw_text, :summary, :category, :severity, :priority,
             :location, :duration, :affected_people, :missing_info, :key_facts,
             :raw_llm_response)
    """
    conn = _get_connection()
    try:
        cursor = conn.execute(sql, row)
        conn.commit()
        get_all_complaints.clear()
        return cursor.lastrowid
    finally:
        conn.close()


@st.cache_data(ttl=60)
def get_all_complaints() -> list[dict]:
    """Return all stored complaints as a list of dicts, newest first (cached for high performance)."""
    conn = _get_connection()
    try:
        cursor = conn.execute("SELECT * FROM complaints ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_complaint_by_id(complaint_id: int) -> dict | None:
    """Return a single complaint record by ID, or None if not found."""
    conn = _get_connection()
    try:
        cursor = conn.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
        row = cursor.fetchone()
        return dict(row) if row is not None else None
    finally:
        conn.close()


def delete_complaint(complaint_id: int) -> bool:
    """
    Delete a single complaint record by ID. Return True if a row was deleted.
    Resets the autoincrement sequence if the database table becomes empty.
    """
    conn = _get_connection()
    try:
        cursor = conn.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
        deleted = cursor.rowcount > 0
        if deleted:
            count = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
            if count == 0:
                try:
                    conn.execute("DELETE FROM sqlite_sequence WHERE name = 'complaints'")
                except sqlite3.OperationalError:
                    pass
        conn.commit()
        get_all_complaints.clear()
        return deleted
    finally:
        conn.close()


def delete_all_complaints() -> int:
    """
    Delete all stored complaints from the database, reset the autoincrement sequence,
    and return the number of deleted rows.
    """
    conn = _get_connection()
    try:
        cursor = conn.execute("DELETE FROM complaints")
        deleted_count = cursor.rowcount
        try:
            conn.execute("DELETE FROM sqlite_sequence WHERE name = 'complaints'")
        except sqlite3.OperationalError:
            pass
        conn.commit()
        get_all_complaints.clear()
        return deleted_count
    finally:
        conn.close()
