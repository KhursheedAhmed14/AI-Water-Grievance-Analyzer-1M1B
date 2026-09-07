"""
tests/test_database.py
Unit tests for database functions in core.database
"""

import unittest
from core.database import (
    delete_all_complaints,
    delete_complaint,
    get_all_complaints,
    get_complaint_by_id,
    insert_complaint,
)


class TestDatabaseFunctions(unittest.TestCase):
    def test_database_crud(self):
        """Test insert, query, single delete, and clear all functionality."""
        sample_record = {
            "summary": "Test complaint for DB operations",
            "category": "Pipeline Leakage",
            "severity": "High",
            "priority": "Urgent",
            "location": "Test Street",
            "duration": "1 day",
            "affected_people": "10",
            "missing_info": "None identified",
            "key_facts": "[\"Test fact 1\"]",
            "raw_text": "Sample test complaint text",
            "raw_llm_response": "{\"summary\": \"Test complaint\"}",
        }

        # 1. Insert complaint
        record_id = insert_complaint(sample_record)
        self.assertIsNotNone(record_id)
        self.assertGreater(record_id, 0)

        # 2. Get by ID
        fetched = get_complaint_by_id(record_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["summary"], "Test complaint for DB operations")

        # 3. Delete single complaint
        deleted_single = delete_complaint(record_id)
        self.assertTrue(deleted_single)
        self.assertIsNone(get_complaint_by_id(record_id))

        # 4. Insert multiple records and delete all
        rec1_id = insert_complaint(sample_record)
        rec2_id = insert_complaint(sample_record)
        self.assertGreaterEqual(len(get_all_complaints()), 2)

        cleared_count = delete_all_complaints()
        self.assertGreaterEqual(cleared_count, 2)
        self.assertEqual(len(get_all_complaints()), 0)

    def test_autoincrement_reset_on_clear(self):
        """Test clearing the database resets auto-increment ID to 1."""
        sample_record = {
            "summary": "Test complaint for autoincrement reset",
            "category": "Water Supply Disruption",
            "severity": "Medium",
            "priority": "High",
            "location": "Reset Avenue",
            "duration": "2 days",
            "affected_people": "5",
            "missing_info": "None identified",
            "key_facts": "[\"Reset test\"]",
            "raw_text": "Autoincrement reset test text",
            "raw_llm_response": "{}",
        }

        # 1. Insert multiple complaints
        id1 = insert_complaint(sample_record)
        id2 = insert_complaint(sample_record)
        self.assertGreater(id2, id1)

        # 2. Clear database completely
        delete_all_complaints()
        self.assertEqual(len(get_all_complaints()), 0)

        # 3. Add one new complaint and verify Record ID is 1
        new_id = insert_complaint(sample_record)
        self.assertEqual(new_id, 1)

        # Cleanup
        delete_all_complaints()


if __name__ == "__main__":
    unittest.main()
