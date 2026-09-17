"""
tests/test_database.py
Unit tests for database functions in core.database.

TEST ISOLATION
--------------
These tests patch core.database.DB_PATH to a temporary SQLite file created
fresh for each test method. The production database (data/grievances.db) is
NEVER opened or touched during test execution.

Isolation guarantee:
  * setUp()   -> creates an OS temp file, redirects DB_PATH to it, calls init_db()
  * tearDown() -> restores DB_PATH to the original value, deletes the temp file

Even if a test raises an unhandled exception, tearDown() still runs (unittest
contract), so the production DB cannot be affected.
"""

import os
import tempfile
import unittest
from pathlib import Path

import core.database as db_module
from core.database import (
    delete_all_complaints,
    delete_complaint,
    get_all_complaints,
    get_complaint_by_id,
    init_db,
    insert_complaint,
)

# ---------------------------------------------------------------------------
# Minimal sample record reused across tests
# ---------------------------------------------------------------------------
_SAMPLE_RECORD = {
    "summary": "Test complaint for DB operations",
    "category": "Pipeline Leakage",
    "severity": "High",
    "priority": "Urgent",
    "location": "Test Street",
    "duration": "1 day",
    "affected_people": "10",
    "missing_info": "None identified",
    "key_facts": '["Test fact 1"]',
    "raw_text": "Sample test complaint text",
    "raw_llm_response": '{"summary": "Test complaint"}',
}


class TestDatabaseFunctions(unittest.TestCase):
    """
    All tests in this class operate on an isolated temporary database.
    The production data/grievances.db is never read or written.
    """

    # ------------------------------------------------------------------
    # Test lifecycle
    # ------------------------------------------------------------------

    def setUp(self):
        """
        1. Create an OS-level temp file (empty, unique per test run).
        2. Close the OS file descriptor immediately so SQLite can own the file.
        3. Redirect core.database.DB_PATH to the temp file path.
        4. Clear the st.cache_data cache so stale results cannot leak between tests.
        5. Call init_db() to create the schema and seed users in the temp DB.
        """
        # mkstemp returns (fd, path); close fd so SQLite can open the file freely
        fd, tmp_path = tempfile.mkstemp(suffix=".db", prefix="test_grievances_")
        os.close(fd)

        self._tmp_path = Path(tmp_path)
        self._original_db_path = db_module.DB_PATH  # save for tearDown

        # Redirect all DB operations to the temp file
        db_module.DB_PATH = self._tmp_path

        # Clear any cached results from previous runs
        try:
            get_all_complaints.clear()
        except Exception:
            pass  # safe to ignore outside a Streamlit runtime

        # Build schema + seed users in the isolated DB
        init_db()

    def tearDown(self):
        """
        1. Clear the cache so no temp-DB results survive into subsequent tests.
        2. Restore core.database.DB_PATH to the original production path.
        3. Delete the temp file.
        """
        try:
            get_all_complaints.clear()
        except Exception:
            pass

        # Restore production path BEFORE deleting the temp file
        db_module.DB_PATH = self._original_db_path

        # Remove the isolated temp DB (missing_ok=True in case already gone)
        try:
            self._tmp_path.unlink(missing_ok=True)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Helper: quick count of complaints in the current (isolated) DB
    # ------------------------------------------------------------------

    def _complaint_count(self) -> int:
        return len(get_all_complaints())

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_database_crud(self):
        """
        Test insert, query, single delete, and clear-all functionality.
        Also validates reference_id generation and uniqueness.
        """
        # 1. Insert a complaint
        record_id, reference_id = insert_complaint(_SAMPLE_RECORD)
        self.assertIsNotNone(record_id)
        self.assertGreater(record_id, 0)
        self.assertIsNotNone(reference_id)
        self.assertTrue(
            reference_id.startswith("WGA-"),
            f"Expected WGA- prefix, got: {reference_id}",
        )

        # 2. Fetch by ID and verify stored fields
        fetched = get_complaint_by_id(record_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["summary"], _SAMPLE_RECORD["summary"])
        self.assertEqual(fetched["reference_id"], reference_id)
        # Default status must be Pending
        self.assertEqual(fetched["status"], "Pending")

        # 3. Single-record delete
        deleted = delete_complaint(record_id)
        self.assertTrue(deleted)
        self.assertIsNone(get_complaint_by_id(record_id))

        # 4. Insert multiple records
        rec1_id, ref1 = insert_complaint(_SAMPLE_RECORD)
        rec2_id, ref2 = insert_complaint(_SAMPLE_RECORD)
        self.assertGreaterEqual(self._complaint_count(), 2)

        # 5. Reference IDs must be unique
        self.assertNotEqual(ref1, ref2)
        self.assertTrue(ref1.startswith("WGA-"))
        self.assertTrue(ref2.startswith("WGA-"))

        # 6. Delete all
        cleared = delete_all_complaints()
        self.assertGreaterEqual(cleared, 2)
        self.assertEqual(self._complaint_count(), 0)

    def test_autoincrement_reset_on_clear(self):
        """
        Test that clearing the database resets the auto-increment ID to 1.
        Validates that insert_complaint() returns (id, reference_id) tuples.
        """
        # Insert two complaints; id2 must be greater than id1
        id1, _ = insert_complaint(_SAMPLE_RECORD)
        id2, _ = insert_complaint(_SAMPLE_RECORD)
        self.assertGreater(id2, id1)

        # Clear database completely
        delete_all_complaints()
        self.assertEqual(self._complaint_count(), 0)

        # After reset, next insert should get id=1
        new_id, new_ref = insert_complaint(_SAMPLE_RECORD)
        self.assertEqual(new_id, 1)
        self.assertTrue(
            new_ref.startswith("WGA-"),
            f"Expected WGA- prefix, got: {new_ref}",
        )

        # Cleanup (also proves tearDown is not the only safeguard)
        delete_all_complaints()

    def test_reference_id_sequential_per_year(self):
        """
        Validate that reference IDs are sequential within the same year
        and that two inserts produce consecutive WGA-YYYY-NNNNN values.
        """
        _, ref_a = insert_complaint(_SAMPLE_RECORD)
        _, ref_b = insert_complaint(_SAMPLE_RECORD)

        # Both must have WGA- prefix
        self.assertTrue(ref_a.startswith("WGA-"))
        self.assertTrue(ref_b.startswith("WGA-"))

        # Extract sequence numbers; they must be consecutive
        seq_a = int(ref_a.split("-")[2])
        seq_b = int(ref_b.split("-")[2])
        self.assertEqual(seq_b, seq_a + 1, "Reference IDs must be strictly sequential")

    def test_municipal_statistics_calculations(self):
        """
        Validate municipal top-level metrics definitions:
        - Total Complaints count
        - High / Urgent count (based on priority: High or Urgent)
        - Pending count (based on status: Pending)
        - Resolved count (based on status: Resolved)
        """
        import pandas as pd
        from core.database import update_complaint_workflow

        # Insert 4 test records with known priorities and statuses
        id1, _ = insert_complaint(dict(_SAMPLE_RECORD, priority="Urgent", summary="Comp 1"))
        id2, _ = insert_complaint(dict(_SAMPLE_RECORD, priority="High", summary="Comp 2"))
        id3, _ = insert_complaint(dict(_SAMPLE_RECORD, priority="Low", summary="Comp 3"))
        id4, _ = insert_complaint(dict(_SAMPLE_RECORD, priority="Medium", summary="Comp 4"))

        # Update status for rec 2 to In Progress, rec 3 to Resolved
        update_complaint_workflow(id2, status="In Progress")
        update_complaint_workflow(id3, status="Resolved")

        complaints = get_all_complaints()
        df = pd.DataFrame(complaints)

        total_count = len(df)
        high_urgent_count = len(df[df["priority"].isin(["High", "Urgent"])])
        pending_count = len(df[df["status"] == "Pending"])
        resolved_count = len(df[df["status"] == "Resolved"])

        self.assertEqual(total_count, 4)
        self.assertEqual(high_urgent_count, 2)  # Urgent (rec1) + High (rec2)
        self.assertEqual(pending_count, 2)      # Pending (rec1, rec4)
        self.assertEqual(resolved_count, 1)     # Resolved (rec3)

    def test_postgres_missing_database_url_validation(self):
        """
        Validate that during application runtime (when DB_PATH is DEFAULT_DB_PATH),
        if DATABASE_URL is missing, _get_connection() raises a clear ValueError configuration error.
        """
        old_url = os.environ.get("DATABASE_URL")
        old_db_path = db_module.DB_PATH
        try:
            if "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

            # Set DB_PATH to default production path to simulate runtime call
            db_module.DB_PATH = db_module.DEFAULT_DB_PATH

            with self.assertRaises(ValueError) as ctx:
                db_module._get_connection()

            self.assertIn("DATABASE_URL environment variable is missing", str(ctx.exception))
        finally:
            db_module.DB_PATH = old_db_path
            if old_url is not None:
                os.environ["DATABASE_URL"] = old_url

    def test_postgres_mode_helper(self):
        """Verify is_postgres_mode() reflects DATABASE_URL state."""
        old_url = os.environ.get("DATABASE_URL")
        try:
            os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/testdb"
            self.assertTrue(db_module.is_postgres_mode())

            del os.environ["DATABASE_URL"]
            self.assertFalse(db_module.is_postgres_mode())
        finally:
            if old_url is not None:
                os.environ["DATABASE_URL"] = old_url


if __name__ == "__main__":
    unittest.main()

