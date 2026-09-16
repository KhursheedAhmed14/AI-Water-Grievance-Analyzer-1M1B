import hashlib
import os
import sqlite3
from datetime import datetime
from pathlib import Path
import streamlit as st

# Resolve DB path relative to the project root, regardless of CWD
DB_PATH = Path(__file__).parent.parent / "data" / "grievances.db"
SALT = b"water_grievance_salt_2026"


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password: str) -> str:
    """Return PBKDF2 HMAC SHA-256 hex string of password."""
    return hashlib.pbkdf2_hmac("sha256", password.strip().encode("utf-8"), SALT, 100000).hex()


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored PBKDF2 hash."""
    return hash_password(password) == stored_hash


# ============================================================
# DATABASE SCHEMA
# ============================================================

CREATE_USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    role            TEXT NOT NULL,
    full_name       TEXT,
    created_at      TEXT
)
"""

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS complaints (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_id        TEXT UNIQUE DEFAULT NULL,
    submitted_at        TEXT,
    raw_text            TEXT,
    summary             TEXT,
    category            TEXT,
    severity            TEXT,
    priority            TEXT,
    location            TEXT,
    duration            TEXT,
    affected_people     TEXT,
    missing_info        TEXT,
    key_facts           TEXT,
    raw_llm_response    TEXT,

    -- Phase 2: Municipal workflow fields
    status              TEXT DEFAULT 'Pending',
    assigned_team       TEXT DEFAULT 'Unassigned',
    municipal_priority  TEXT DEFAULT NULL,
    review_notes        TEXT DEFAULT '',
    resolved_at         TEXT DEFAULT NULL,

    -- Citizen Ownership
    citizen_id          INTEGER DEFAULT NULL REFERENCES users(id)
)
"""


# ============================================================
# CONNECTION
# ============================================================

def _get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with Row-based results."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# DATABASE INITIALIZATION / MIGRATION
# ============================================================

def generate_reference_id(year: int, conn: sqlite3.Connection) -> str:
    """
    Generate the next sequential citizen-facing reference ID for the given year.

    Format: WGA-YYYY-NNNNN
    The sequence number is based on the count of complaints already having a
    reference_id for that year, so deletions do not create gaps in future IDs
    and the counter is never derived from the raw auto-increment `id`.

    The caller is responsible for passing an open connection so this can run
    inside the same transaction as the INSERT, preventing race conditions.
    """
    year_prefix = f"{year:04d}-"
    count_row = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE reference_id LIKE ?",
        (f"WGA-{year_prefix}%",),
    ).fetchone()
    next_seq = (count_row[0] if count_row else 0) + 1
    return f"WGA-{year:04d}-{next_seq:05d}"


def init_db() -> None:
    """
    Create database tables if needed, seed demo users, and safely
    migrate existing databases to include citizen_id, Phase 2 fields,
    and the reference_id column (with backfill for existing records).
    """
    os.makedirs(DB_PATH.parent, exist_ok=True)

    conn = _get_connection()

    try:
        # Create users & complaints tables for a fresh database
        conn.execute(CREATE_USERS_TABLE_SQL)
        conn.execute(CREATE_TABLE_SQL)

        # Seed initial demo accounts if users table is empty
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count == 0:
            now_iso = datetime.utcnow().isoformat()
            seed_users = [
                ("citizen@example.com", hash_password("citizen123"), "citizen", "Citizen Demo"),
                ("officer", hash_password("water2026"), "municipal", "Municipal Officer"),
                ("admin", hash_password("admin123"), "municipal", "System Admin"),
            ]
            for u, p_hash, r, name in seed_users:
                conn.execute(
                    "INSERT OR IGNORE INTO users (username, password_hash, role, full_name, created_at) VALUES (?, ?, ?, ?, ?)",
                    (u, p_hash, r, name, now_iso),
                )

        # ----------------------------------------------------
        # Column migration for existing databases
        # ----------------------------------------------------
        existing_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(complaints)").fetchall()
        }

        all_new_columns = {
            "status": "TEXT DEFAULT 'Pending'",
            "assigned_team": "TEXT DEFAULT 'Unassigned'",
            "municipal_priority": "TEXT DEFAULT NULL",
            "review_notes": "TEXT DEFAULT ''",
            "resolved_at": "TEXT DEFAULT NULL",
            "citizen_id": "INTEGER DEFAULT NULL REFERENCES users(id)",
            # NOTE: SQLite does not allow ADD COLUMN ... UNIQUE.
            # We add the column without UNIQUE here and create the index below.
            "reference_id": "TEXT DEFAULT NULL",
        }

        for column_name, column_definition in all_new_columns.items():
            if column_name not in existing_columns:
                conn.execute(
                    f"ALTER TABLE complaints "
                    f"ADD COLUMN {column_name} {column_definition}"
                )

        # Ensure unique index on reference_id exists (safe to run repeatedly)
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_complaints_reference_id "
            "ON complaints (reference_id)"
        )

        conn.execute("""
            UPDATE complaints
            SET status = 'Pending'
            WHERE status IS NULL OR status = ''
        """)

        conn.execute("""
            UPDATE complaints
            SET assigned_team = 'Unassigned'
            WHERE assigned_team IS NULL OR assigned_team = ''
        """)

        # ----------------------------------------------------
        # Backfill reference_id for existing records that lack one.
        # Process in ascending id order so older records get lower numbers.
        # submitted_at is stored as ISO-8601 text (e.g. '2026-09-12T10:11:22.961617');
        # we extract the year with substr(submitted_at, 1, 4).
        # ----------------------------------------------------
        unref_rows = conn.execute(
            "SELECT id, submitted_at FROM complaints "
            "WHERE reference_id IS NULL "
            "ORDER BY id ASC"
        ).fetchall()

        for row in unref_rows:
            rec_id = row[0]
            submitted_at_str = row[1] or ""
            try:
                year = int(submitted_at_str[:4])
            except (ValueError, TypeError):
                year = datetime.utcnow().year

            ref_id = generate_reference_id(year, conn)
            conn.execute(
                "UPDATE complaints SET reference_id = ? WHERE id = ?",
                (ref_id, rec_id),
            )

        conn.commit()

    finally:
        conn.close()


# ============================================================
# USER MANAGEMENT & AUTHENTICATION (DATABASE)
# ============================================================

def create_user(username: str, password: str, role: str = "citizen", full_name: str = "") -> tuple[bool, str, int | None]:
    """Create a new user account with PBKDF2 hashed password."""
    u_clean = username.strip().lower()
    p_clean = password.strip()
    if not u_clean or not p_clean:
        return False, "Username/Email and password are required.", None

    conn = _get_connection()
    try:
        existing = conn.execute("SELECT id FROM users WHERE username = ?", (u_clean,)).fetchone()
        if existing:
            return False, "An account with this email/username already exists.", None

        now_iso = datetime.utcnow().isoformat()
        p_hash = hash_password(p_clean)
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, role, full_name, created_at) VALUES (?, ?, ?, ?, ?)",
            (u_clean, p_hash, role, full_name.strip(), now_iso),
        )
        conn.commit()
        return True, "User registered successfully.", cursor.lastrowid
    except sqlite3.IntegrityError:
        return False, "User creation failed due to username conflict.", None
    finally:
        conn.close()


def get_user_by_username(username: str) -> dict | None:
    """Fetch a user record by username/email."""
    conn = _get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username.strip().lower(),)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def authenticate_user(username: str, password: str, required_role: str | None = None) -> dict | None:
    """Verify user credentials and return user dict on success, None on failure."""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    if required_role and user["role"] != required_role:
        return None
    return user


# ============================================================
# PHASE 1 & 2: COMPLAINT STORAGE (CITIZEN OWNERSHIP)
# ============================================================

def insert_complaint(record: dict, citizen_id: int | None = None) -> tuple[int, str]:
    """
    Store a fully analyzed complaint and return (record_id, reference_id).

    Phase 1 AI fields and Phase 2 municipal workflow fields are preserved.
    Links complaint to submitting citizen_id if provided.

    A unique citizen-facing reference_id (WGA-YYYY-NNNNN) is generated
    inside the same connection as the INSERT to prevent duplicates.
    The sequence number is year-based and counts existing reference IDs
    for that year, so gaps from deletions do not affect future numbering.
    """
    c_id = citizen_id if citizen_id is not None else record.get("citizen_id")

    submitted_at = record.get("submitted_at") or datetime.utcnow().isoformat()
    try:
        year = int(submitted_at[:4])
    except (ValueError, TypeError):
        year = datetime.utcnow().year

    row = {
        "submitted_at": submitted_at,
        "raw_text": record.get("raw_text"),
        "summary": record.get("summary"),
        "category": record.get("category"),
        "severity": record.get("severity"),
        "priority": record.get("priority"),
        "location": record.get("location"),
        "duration": record.get("duration"),
        "affected_people": record.get("affected_people"),
        "missing_info": record.get("missing_info"),
        "key_facts": record.get("key_facts"),
        "raw_llm_response": record.get("raw_llm_response"),

        # Phase 2 defaults
        "status": record.get("status", "Pending"),
        "assigned_team": record.get("assigned_team", "Unassigned"),
        "municipal_priority": record.get("municipal_priority"),
        "review_notes": record.get("review_notes", ""),
        "resolved_at": record.get("resolved_at"),
        "citizen_id": c_id,
    }

    sql = """
        INSERT INTO complaints
            (
                reference_id,
                submitted_at,
                raw_text,
                summary,
                category,
                severity,
                priority,
                location,
                duration,
                affected_people,
                missing_info,
                key_facts,
                raw_llm_response,
                status,
                assigned_team,
                municipal_priority,
                review_notes,
                resolved_at,
                citizen_id
            )
        VALUES
            (
                :reference_id,
                :submitted_at,
                :raw_text,
                :summary,
                :category,
                :severity,
                :priority,
                :location,
                :duration,
                :affected_people,
                :missing_info,
                :key_facts,
                :raw_llm_response,
                :status,
                :assigned_team,
                :municipal_priority,
                :review_notes,
                :resolved_at,
                :citizen_id
            )
    """

    conn = _get_connection()

    try:
        # Generate reference_id inside the same connection/transaction so the
        # count used for sequencing and the INSERT are atomic.
        reference_id = generate_reference_id(year, conn)
        row["reference_id"] = reference_id

        cursor = conn.execute(sql, row)
        conn.commit()

        clear_db_caches()

        return cursor.lastrowid, reference_id

    finally:
        conn.close()


def clear_db_caches():
    """Clear all Streamlit cached database read operations to prevent stale UI state."""
    try:
        get_all_complaints.clear()
    except Exception:
        pass
    try:
        get_complaints_by_citizen.clear()
    except Exception:
        pass
    try:
        get_complaint_by_id.clear()
    except Exception:
        pass


# ============================================================
# READ OPERATIONS
# ============================================================

@st.cache_data(ttl=60)
def get_all_complaints() -> list[dict]:
    """
    Return all complaints across all citizens, newest first.
    Used by Municipal Officers for triage.
    """
    conn = _get_connection()

    try:
        cursor = conn.execute(
            "SELECT * FROM complaints ORDER BY id DESC"
        )

        return [dict(row) for row in cursor.fetchall()]

    finally:
        conn.close()


@st.cache_data(ttl=60)
def get_complaints_by_citizen(citizen_id: int) -> list[dict]:
    """
    Return complaints submitted by a specific citizen_id, newest first.
    Enforces citizen complaint ownership for the Citizen Portal.
    """
    if not citizen_id:
        return []

    conn = _get_connection()

    try:
        cursor = conn.execute(
            "SELECT * FROM complaints WHERE citizen_id = ? ORDER BY id DESC",
            (citizen_id,)
        )

        return [dict(row) for row in cursor.fetchall()]

    finally:
        conn.close()


@st.cache_data(ttl=60)
def get_complaint_by_id(complaint_id: int) -> dict | None:
    """Return one complaint by ID."""
    conn = _get_connection()

    try:
        cursor = conn.execute(
            "SELECT * FROM complaints WHERE id = ?",
            (complaint_id,)
        )

        row = cursor.fetchone()

        return dict(row) if row is not None else None

    finally:
        conn.close()


# ============================================================
# PHASE 2: MUNICIPAL WORKFLOW
# ============================================================

# Sentinel used by update_complaint_workflow to distinguish
# "caller did not provide this field" from "caller wants to set it to NULL".
_UNSET = object()


def update_complaint_workflow(
    complaint_id: int,
    status: str | None = None,
    assigned_team: str | None = None,
    municipal_priority: object = _UNSET,  # _UNSET = skip; None = clear to NULL
    review_notes: str | None = None,
    resolved_at: str | None = None,
) -> bool:
    """
    Update municipal workflow fields for a complaint.

    Only fields explicitly provided are updated.
    Pass municipal_priority=None explicitly to clear it back to NULL
    (i.e. when the officer resets to 'Not Set').
    Omitting municipal_priority entirely leaves the stored value unchanged.
    Returns True if the complaint exists and was updated.
    """

    updates = []
    values = []

    if status is not None:
        updates.append("status = ?")
        values.append(status)

    if assigned_team is not None:
        updates.append("assigned_team = ?")
        values.append(assigned_team)

    if municipal_priority is not _UNSET:
        # Explicitly provided (even if None) — update the column.
        updates.append("municipal_priority = ?")
        values.append(municipal_priority)  # None → SQL NULL

    if review_notes is not None:
        updates.append("review_notes = ?")
        values.append(review_notes)

    if resolved_at is not None:
        updates.append("resolved_at = ?")
        values.append(resolved_at)

    if not updates:
        return False

    values.append(complaint_id)

    sql = f"""
        UPDATE complaints
        SET {", ".join(updates)}
        WHERE id = ?
    """

    conn = _get_connection()

    try:
        cursor = conn.execute(sql, values)
        conn.commit()

        clear_db_caches()

        return cursor.rowcount > 0

    finally:
        conn.close()


def assign_complaint(
    complaint_id: int,
    assigned_team: str,
) -> bool:
    """
    Assign a complaint to a municipal team.
    Automatically changes status to Assigned.
    """
    return update_complaint_workflow(
        complaint_id=complaint_id,
        assigned_team=assigned_team,
        status="Assigned",
    )


def update_complaint_status(
    complaint_id: int,
    status: str,
) -> bool:
    """Update the municipal workflow status."""
    resolved_at = None

    if status == "Resolved":
        resolved_at = datetime.utcnow().isoformat()

    return update_complaint_workflow(
        complaint_id=complaint_id,
        status=status,
        resolved_at=resolved_at,
    )


def save_municipal_review(
    complaint_id: int,
    municipal_priority: str,
    review_notes: str = "",
) -> bool:
    """
    Save the final municipal priority and review notes.
    This represents human review, not AI recommendation.
    """
    return update_complaint_workflow(
        complaint_id=complaint_id,
        municipal_priority=municipal_priority,
        review_notes=review_notes,
    )


# ============================================================
# DELETE OPERATIONS
# ============================================================

def delete_complaint(complaint_id: int) -> bool:
    """
    Delete a single complaint.

    If the database becomes empty, reset the AUTOINCREMENT sequence.
    """
    conn = _get_connection()

    try:
        cursor = conn.execute(
            "DELETE FROM complaints WHERE id = ?",
            (complaint_id,)
        )

        deleted = cursor.rowcount > 0

        if deleted:
            count = conn.execute(
                "SELECT COUNT(*) FROM complaints"
            ).fetchone()[0]

            if count == 0:
                try:
                    conn.execute(
                        "DELETE FROM sqlite_sequence "
                        "WHERE name = 'complaints'"
                    )
                except sqlite3.OperationalError:
                    pass

        conn.commit()

        clear_db_caches()

        return deleted

    finally:
        conn.close()


def delete_all_complaints() -> int:
    """
    Delete all complaints and reset the AUTOINCREMENT sequence.
    """
    conn = _get_connection()

    try:
        cursor = conn.execute(
            "DELETE FROM complaints"
        )

        deleted_count = cursor.rowcount

        try:
            conn.execute(
                "DELETE FROM sqlite_sequence "
                "WHERE name = 'complaints'"
            )
        except sqlite3.OperationalError:
            pass

        conn.commit()

        clear_db_caches()

        return deleted_count

    finally:
        conn.close()