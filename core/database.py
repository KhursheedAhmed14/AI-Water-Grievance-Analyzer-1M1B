import hashlib
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st

# Optional PostgreSQL driver support via psycopg (v3)
try:
    import psycopg
    from psycopg.rows import dict_row
    from psycopg.errors import IntegrityError as PgIntegrityError, OperationalError as PgOperationalError
    HAS_PSYCOPG = True
except ImportError:
    psycopg = None
    dict_row = None
    PgIntegrityError = None
    PgOperationalError = None
    HAS_PSYCOPG = False

# Resolve SQLite DB path relative to the project root for isolated unit testing
DEFAULT_DB_PATH = Path(__file__).parent.parent / "data" / "grievances.db"
DB_PATH = DEFAULT_DB_PATH
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
# DATABASE SCHEMAS (POSTGRESQL & SQLITE COMPATIBLE)
# ============================================================

CREATE_USERS_TABLE_PG = """
CREATE TABLE IF NOT EXISTS users (
    id              BIGSERIAL PRIMARY KEY,
    username        VARCHAR(255) UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    role            VARCHAR(50) NOT NULL,
    full_name       TEXT,
    created_at      TEXT
);
"""

CREATE_COMPLAINTS_TABLE_PG = """
CREATE TABLE IF NOT EXISTS complaints (
    id                  BIGSERIAL PRIMARY KEY,
    reference_id        VARCHAR(255) UNIQUE DEFAULT NULL,
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
    status              TEXT DEFAULT 'Pending',
    assigned_team       TEXT DEFAULT 'Unassigned',
    municipal_priority  TEXT DEFAULT NULL,
    review_notes        TEXT DEFAULT '',
    resolved_at         TEXT DEFAULT NULL,
    citizen_id          BIGINT DEFAULT NULL REFERENCES users(id) ON DELETE SET NULL
);
"""

CREATE_REF_SEQ_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS reference_id_sequences (
    year INT PRIMARY KEY,
    last_seq INT NOT NULL DEFAULT 0
);
"""

CREATE_USERS_TABLE_SQLITE = """
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    role            TEXT NOT NULL,
    full_name       TEXT,
    created_at      TEXT
);
"""

CREATE_COMPLAINTS_TABLE_SQLITE = """
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
    status              TEXT DEFAULT 'Pending',
    assigned_team       TEXT DEFAULT 'Unassigned',
    municipal_priority  TEXT DEFAULT NULL,
    review_notes        TEXT DEFAULT '',
    resolved_at         TEXT DEFAULT NULL,
    citizen_id          INTEGER DEFAULT NULL REFERENCES users(id)
);
"""


# ============================================================
# UNIFIED DATABASE CONNECTION & WRAPPER
# ============================================================

def is_postgres_mode() -> bool:
    """Return True if DATABASE_URL environment variable is set."""
    db_url = os.getenv("DATABASE_URL", "").strip()
    return bool(db_url)


class DBWrapperCursor:
    """Cursor wrapper for dict-style row access and normalized rowcount/lastrowid."""

    def __init__(self, cursor, is_pg: bool):
        self.cursor = cursor
        self.is_pg = is_pg

    def fetchone(self) -> dict | None:
        row = self.cursor.fetchone()
        if row is None:
            return None
        if isinstance(row, dict):
            return row
        return dict(row)

    def fetchall(self) -> list[dict]:
        rows = self.cursor.fetchall()
        if not rows:
            return []
        return [dict(r) if not isinstance(r, dict) else r for r in rows]

    @property
    def rowcount(self) -> int:
        return getattr(self.cursor, "rowcount", -1)

    @property
    def lastrowid(self) -> int | None:
        if hasattr(self.cursor, "lastrowid") and self.cursor.lastrowid is not None:
            return self.cursor.lastrowid
        return None


class DBWrapper:
    """
    Unified database connection wrapper around psycopg (PostgreSQL) or sqlite3.
    Normalizes SQL placeholders (%s vs ? and %(name)s vs :name) and row representations.
    """

    def __init__(self, raw_conn, is_pg: bool):
        self.raw_conn = raw_conn
        self.is_pg = is_pg

    def _normalize_sql(self, sql: str, params: tuple | list | dict | None) -> tuple[str, tuple | list | dict | None]:
        if params is None:
            params = ()

        if self.is_pg:
            # Convert SQLite placeholders (:key -> %(key)s and ? -> %s) if needed
            if isinstance(params, dict):
                sql_norm = re.sub(r'(?<!%):([a-zA-Z0-9_]+)', r'%(\1)s', sql)
                return sql_norm, params
            elif isinstance(params, (list, tuple)):
                sql_norm = sql.replace('?', '%s')
                return sql_norm, params
        else:
            # Convert PostgreSQL placeholders (%(key)s -> :key and %s -> ?) if needed
            if isinstance(params, dict):
                sql_norm = re.sub(r'%\(([a-zA-Z0-9_]+)\)s', r':\1', sql)
                return sql_norm, params
            elif isinstance(params, (list, tuple)):
                sql_norm = sql.replace('%s', '?')
                return sql_norm, params

        return sql, params

    def execute(self, sql: str, params: tuple | list | dict | None = None) -> DBWrapperCursor:
        sql_norm, params_norm = self._normalize_sql(sql, params)
        if self.is_pg:
            cursor = self.raw_conn.execute(sql_norm, params_norm or ())
        else:
            cursor = self.raw_conn.execute(sql_norm, params_norm or ())
        return DBWrapperCursor(cursor, is_pg=self.is_pg)

    def commit(self) -> None:
        if not self.is_pg:
            self.raw_conn.commit()
        else:
            self.raw_conn.commit()

    def close(self) -> None:
        self.raw_conn.close()


def _connect_pg_with_fallback(db_url: str):
    """Attempt psycopg.connect(db_url). If local DNS resolution fails on Windows, fallback to resolved IPv4 hostaddr."""
    try:
        return psycopg.connect(db_url, row_factory=dict_row)
    except Exception as e:
        if "getaddrinfo failed" in str(e):
            from urllib.parse import urlparse
            import socket
            import subprocess
            try:
                parsed = urlparse(db_url)
                hostname = parsed.hostname
                if hostname:
                    try:
                        resolved_ip = socket.gethostbyname(hostname)
                        return psycopg.connect(db_url, hostaddr=resolved_ip, row_factory=dict_row)
                    except Exception:
                        pass
                    res = subprocess.run(["nslookup", hostname, "8.8.8.8"], capture_output=True, text=True, timeout=3)
                    ips = re.findall(r"([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", res.stdout)
                    valid_ips = [ip for ip in ips if not ip.startswith("8.8.8")]
                    if valid_ips:
                        return psycopg.connect(db_url, hostaddr=valid_ips[-1], row_factory=dict_row)
            except Exception:
                pass
        raise e


def _get_connection() -> DBWrapper:
    """
    Return a unified database connection.
    Uses PostgreSQL via psycopg if DATABASE_URL environment variable is set.

    In application runtime, DATABASE_URL is strictly required. If DATABASE_URL is missing,
    a clear ValueError configuration error is raised. SQLite fallback is restricted
    EXCLUSIVELY to isolated unit tests (where DB_PATH is explicitly redirected to a temp file).
    """
    db_url = os.getenv("DATABASE_URL", "").strip()

    if db_url:
        if not HAS_PSYCOPG:
            raise RuntimeError(
                "PostgreSQL configuration detected in DATABASE_URL, but the 'psycopg' driver is not installed. "
                "Please install psycopg[binary]."
            )
        try:
            conn = _connect_pg_with_fallback(db_url)
            return DBWrapper(conn, is_pg=True)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to PostgreSQL database via DATABASE_URL: {e}") from e

    # Check if we are running in an isolated unit test environment
    is_test_environment = (DB_PATH != DEFAULT_DB_PATH) or (os.getenv("TESTING", "").lower() in ("1", "true", "yes"))

    if not is_test_environment:
        raise ValueError(
            "Configuration Error: DATABASE_URL environment variable is missing. "
            "Please configure DATABASE_URL in your environment or .env file to run the application with PostgreSQL."
        )

    # Isolated unit test execution on temporary SQLite DB
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return DBWrapper(conn, is_pg=False)


# ============================================================
# ATOMIC REFERENCE ID GENERATION
# ============================================================

def generate_reference_id(year: int, conn: DBWrapper) -> str:
    """
    Generate the next sequential citizen-facing reference ID for the given year.

    Format: WGA-YYYY-NNNNN

    Thread-safe & Process-safe: Uses an atomic sequence table with
    `ON CONFLICT (year) DO UPDATE SET last_seq = last_seq + 1 RETURNING last_seq`
    in PostgreSQL / SQLite, eliminating race conditions under concurrent inserts.
    """
    if conn.is_pg:
        sql = """
            INSERT INTO reference_id_sequences (year, last_seq)
            VALUES (%s, 1)
            ON CONFLICT (year)
            DO UPDATE SET last_seq = reference_id_sequences.last_seq + 1
            RETURNING last_seq;
        """
        row = conn.execute(sql, (year,)).fetchone()
        next_seq = row["last_seq"] if row else 1
    else:
        # SQLite fallback handling
        sql_upsert = """
            INSERT INTO reference_id_sequences (year, last_seq)
            VALUES (?, 1)
            ON CONFLICT (year)
            DO UPDATE SET last_seq = last_seq + 1
            RETURNING last_seq;
        """
        try:
            row = conn.execute(sql_upsert, (year,)).fetchone()
            next_seq = row["last_seq"] if row else 1
        except Exception:
            # Older SQLite fallback without RETURNING
            count_row = conn.execute(
                "SELECT COUNT(*) as count FROM complaints WHERE reference_id LIKE ?",
                (f"WGA-{year:04d}-%",),
            ).fetchone()
            next_seq = (count_row["count"] if count_row else 0) + 1

    return f"WGA-{year:04d}-{next_seq:05d}"


# ============================================================
# DATABASE INITIALIZATION / MIGRATION
# ============================================================

def init_db() -> None:
    """
    Create database tables if needed, seed demo users, and safely
    migrate existing databases to include citizen_id, Phase 2 fields,
    and reference_id sequences.
    """
    conn = _get_connection()

    try:
        if conn.is_pg:
            conn.execute(CREATE_USERS_TABLE_PG)
            conn.execute(CREATE_COMPLAINTS_TABLE_PG)
            conn.execute(CREATE_REF_SEQ_TABLE_SQL)

            # Seed demo accounts if users table is empty
            user_count_row = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
            user_count = user_count_row["cnt"] if user_count_row else 0
            if user_count == 0:
                now_iso = datetime.now(timezone.utc).isoformat()
                seed_users = [
                    ("citizen@example.com", hash_password("citizen123"), "citizen", "Citizen Demo"),
                    ("officer", hash_password("water2026"), "municipal", "Municipal Officer"),
                    ("admin", hash_password("admin123"), "municipal", "System Admin"),
                ]
                for u, p_hash, r, name in seed_users:
                    conn.execute(
                        "INSERT INTO users (username, password_hash, role, full_name, created_at) "
                        "VALUES (%s, %s, %s, %s, %s) ON CONFLICT (username) DO NOTHING",
                        (u, p_hash, r, name, now_iso),
                    )

            # Schema columns check for PostgreSQL
            cols_rows = conn.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'complaints'"
            ).fetchall()
            existing_columns = {r["column_name"] for r in cols_rows}
        else:
            conn.execute(CREATE_USERS_TABLE_SQLITE)
            conn.execute(CREATE_COMPLAINTS_TABLE_SQLITE)
            conn.execute(CREATE_REF_SEQ_TABLE_SQL)

            user_count_row = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
            user_count = user_count_row["cnt"] if user_count_row else 0
            if user_count == 0:
                now_iso = datetime.now(timezone.utc).isoformat()
                seed_users = [
                    ("citizen@example.com", hash_password("citizen123"), "citizen", "Citizen Demo"),
                    ("officer", hash_password("water2026"), "municipal", "Municipal Officer"),
                    ("admin", hash_password("admin123"), "municipal", "System Admin"),
                ]
                for u, p_hash, r, name in seed_users:
                    conn.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role, full_name, created_at) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (u, p_hash, r, name, now_iso),
                    )

            cols_rows = conn.execute("PRAGMA table_info(complaints)").fetchall()
            existing_columns = {r["name"] for r in cols_rows}

        # ----------------------------------------------------
        # Column migration for existing databases
        # ----------------------------------------------------
        all_new_columns = {
            "status": "TEXT DEFAULT 'Pending'",
            "assigned_team": "TEXT DEFAULT 'Unassigned'",
            "municipal_priority": "TEXT DEFAULT NULL",
            "review_notes": "TEXT DEFAULT ''",
            "resolved_at": "TEXT DEFAULT NULL",
            "citizen_id": "BIGINT DEFAULT NULL" if conn.is_pg else "INTEGER DEFAULT NULL REFERENCES users(id)",
            "reference_id": "TEXT DEFAULT NULL",
        }

        for column_name, column_definition in all_new_columns.items():
            if column_name not in existing_columns:
                conn.execute(
                    f"ALTER TABLE complaints ADD COLUMN {column_name} {column_definition}"
                )

        # Unique index on reference_id
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

        # Sync reference_id_sequences table from existing records
        unref_rows = conn.execute(
            "SELECT id, submitted_at FROM complaints WHERE reference_id IS NULL ORDER BY id ASC"
        ).fetchall()

        for row in unref_rows:
            rec_id = row["id"]
            submitted_at_str = row.get("submitted_at") or ""
            try:
                year = int(submitted_at_str[:4])
            except (ValueError, TypeError):
                year = datetime.now(timezone.utc).year

            ref_id = generate_reference_id(year, conn)
            conn.execute(
                "UPDATE complaints SET reference_id = %s WHERE id = %s",
                (ref_id, rec_id),
            )

        conn.commit()

    finally:
        conn.close()


# ============================================================
# USER MANAGEMENT & AUTHENTICATION
# ============================================================

def create_user(username: str, password: str, role: str = "citizen", full_name: str = "") -> tuple[bool, str, int | None]:
    """Create a new user account with PBKDF2 hashed password."""
    u_clean = username.strip().lower()
    p_clean = password.strip()
    if not u_clean or not p_clean:
        return False, "Username/Email and password are required.", None

    conn = _get_connection()
    try:
        existing = conn.execute("SELECT id FROM users WHERE username = %s", (u_clean,)).fetchone()
        if existing:
            return False, "An account with this email/username already exists.", None

        now_iso = datetime.now(timezone.utc).isoformat()
        p_hash = hash_password(p_clean)
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, role, full_name, created_at) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (u_clean, p_hash, role, full_name.strip(), now_iso),
        )
        row = cursor.fetchone()
        new_id = row["id"] if (row and "id" in row) else cursor.lastrowid
        conn.commit()
        return True, "User registered successfully.", new_id
    except Exception as exc:
        is_integrity = isinstance(exc, sqlite3.IntegrityError) or (PgIntegrityError and isinstance(exc, PgIntegrityError))
        if is_integrity or "unique" in str(exc).lower():
            return False, "User creation failed due to username conflict.", None
        raise exc
    finally:
        conn.close()


def get_user_by_username(username: str) -> dict | None:
    """Fetch a user record by username/email."""
    conn = _get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE username = %s", (username.strip().lower(),)).fetchone()
        return row if row else None
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
# COMPLAINT STORAGE (PHASE 1 & Phase 2)
# ============================================================

def insert_complaint(record: dict, citizen_id: int | None = None) -> tuple[int, str]:
    """
    Store a fully analyzed complaint and return (record_id, reference_id).

    Preserves AI extraction fields and municipal workflow fields.
    Generates an atomic, unique citizen-facing reference ID (WGA-YYYY-NNNNN).
    """
    c_id = citizen_id if citizen_id is not None else record.get("citizen_id")

    submitted_at = record.get("submitted_at") or datetime.now(timezone.utc).isoformat()
    try:
        year = int(submitted_at[:4])
    except (ValueError, TypeError):
        year = datetime.now(timezone.utc).year

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
                %(reference_id)s,
                %(submitted_at)s,
                %(raw_text)s,
                %(summary)s,
                %(category)s,
                %(severity)s,
                %(priority)s,
                %(location)s,
                %(duration)s,
                %(affected_people)s,
                %(missing_info)s,
                %(key_facts)s,
                %(raw_llm_response)s,
                %(status)s,
                %(assigned_team)s,
                %(municipal_priority)s,
                %(review_notes)s,
                %(resolved_at)s,
                %(citizen_id)s
            )
        RETURNING id;
    """

    conn = _get_connection()

    try:
        reference_id = generate_reference_id(year, conn)
        row["reference_id"] = reference_id

        cursor = conn.execute(sql, row)
        res_row = cursor.fetchone()
        new_id = res_row["id"] if (res_row and "id" in res_row) else cursor.lastrowid
        conn.commit()

        clear_db_caches()

        return new_id, reference_id

    finally:
        conn.close()


def clear_db_caches() -> None:
    """Clear Streamlit cached database read operations."""
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
    """Return all complaints across all citizens, newest first."""
    conn = _get_connection()
    try:
        cursor = conn.execute("SELECT * FROM complaints ORDER BY id DESC")
        return cursor.fetchall()
    finally:
        conn.close()


@st.cache_data(ttl=60)
def get_complaints_by_citizen(citizen_id: int) -> list[dict]:
    """Return complaints submitted by a specific citizen_id, newest first."""
    if not citizen_id:
        return []

    conn = _get_connection()
    try:
        cursor = conn.execute(
            "SELECT * FROM complaints WHERE citizen_id = %s ORDER BY id DESC",
            (citizen_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()


@st.cache_data(ttl=60)
def get_complaint_by_id(complaint_id: int) -> dict | None:
    """Return one complaint by ID."""
    conn = _get_connection()
    try:
        cursor = conn.execute("SELECT * FROM complaints WHERE id = %s", (complaint_id,))
        return cursor.fetchone()
    finally:
        conn.close()


# ============================================================
# MUNICIPAL WORKFLOW OPERATIONS
# ============================================================

_UNSET = object()


def update_complaint_workflow(
    complaint_id: int,
    status: str | None = None,
    assigned_team: str | None = None,
    municipal_priority: object = _UNSET,
    review_notes: str | None = None,
    resolved_at: str | None = None,
) -> bool:
    """Update municipal workflow fields for a complaint."""

    updates = []
    values = []

    if status is not None:
        updates.append("status = %s")
        values.append(status)

    if assigned_team is not None:
        updates.append("assigned_team = %s")
        values.append(assigned_team)

    if municipal_priority is not _UNSET:
        updates.append("municipal_priority = %s")
        values.append(municipal_priority)

    if review_notes is not None:
        updates.append("review_notes = %s")
        values.append(review_notes)

    if resolved_at is not None:
        updates.append("resolved_at = %s")
        values.append(resolved_at)

    if not updates:
        return False

    values.append(complaint_id)

    sql = f"""
        UPDATE complaints
        SET {", ".join(updates)}
        WHERE id = %s
    """

    conn = _get_connection()

    try:
        cursor = conn.execute(sql, values)
        conn.commit()

        clear_db_caches()

        return cursor.rowcount > 0

    finally:
        conn.close()


def assign_complaint(complaint_id: int, assigned_team: str) -> bool:
    """Assign a complaint to a municipal team."""
    return update_complaint_workflow(
        complaint_id=complaint_id,
        assigned_team=assigned_team,
        status="Assigned",
    )


def update_complaint_status(complaint_id: int, status: str) -> bool:
    """Update municipal workflow status."""
    resolved_at = None
    if status == "Resolved":
        resolved_at = datetime.now(timezone.utc).isoformat()

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
    """Save municipal priority and review notes."""
    return update_complaint_workflow(
        complaint_id=complaint_id,
        municipal_priority=municipal_priority,
        review_notes=review_notes,
    )


# ============================================================
# DELETE OPERATIONS
# ============================================================

def delete_complaint(complaint_id: int) -> bool:
    """Delete a single complaint."""
    conn = _get_connection()

    try:
        cursor = conn.execute("DELETE FROM complaints WHERE id = %s", (complaint_id,))
        deleted = cursor.rowcount > 0

        if deleted:
            count_row = conn.execute("SELECT COUNT(*) as cnt FROM complaints").fetchone()
            count = count_row["cnt"] if count_row else 0

            if count == 0:
                try:
                    if conn.is_pg:
                        conn.execute("ALTER SEQUENCE complaints_id_seq RESTART WITH 1;")
                        conn.execute("DELETE FROM reference_id_sequences;")
                    else:
                        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'complaints'")
                        conn.execute("DELETE FROM reference_id_sequences;")
                except Exception:
                    pass

        conn.commit()
        clear_db_caches()
        return deleted

    finally:
        conn.close()


def delete_all_complaints() -> int:
    """Delete all complaints and reset auto-increment sequences."""
    conn = _get_connection()

    try:
        cursor = conn.execute("DELETE FROM complaints")
        deleted_count = cursor.rowcount

        try:
            if conn.is_pg:
                conn.execute("ALTER SEQUENCE complaints_id_seq RESTART WITH 1;")
                conn.execute("DELETE FROM reference_id_sequences;")
            else:
                conn.execute("DELETE FROM sqlite_sequence WHERE name = 'complaints'")
                conn.execute("DELETE FROM reference_id_sequences;")
        except Exception:
            pass

        conn.commit()
        clear_db_caches()
        return deleted_count

    finally:
        conn.close()