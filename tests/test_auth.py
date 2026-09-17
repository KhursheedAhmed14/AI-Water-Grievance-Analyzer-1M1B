"""
tests/test_auth.py
Unit tests for core.auth dual-role prototype authentication functions.
"""

import os
import tempfile
import unittest
from pathlib import Path
import streamlit as st
import core.database as db_module
from core.database import init_db
from core.auth import (
    get_authenticated_user,
    get_current_role,
    is_citizen_authenticated,
    is_municipal_authenticated,
    login_citizen,
    login_municipal,
    logout,
)


class TestAuthFunctions(unittest.TestCase):
    def setUp(self):
        fd, tmp_path = tempfile.mkstemp(suffix=".db", prefix="test_auth_")
        os.close(fd)
        self._tmp_path = Path(tmp_path)
        self._original_db_path = db_module.DB_PATH
        db_module.DB_PATH = self._tmp_path

        init_db()
        st.session_state.clear()

    def tearDown(self):
        db_module.DB_PATH = self._original_db_path
        try:
            self._tmp_path.unlink(missing_ok=True)
        except Exception:
            pass

    def test_initial_state(self):
        self.assertIsNone(get_current_role())
        self.assertFalse(is_citizen_authenticated())
        self.assertFalse(is_municipal_authenticated())
        self.assertIsNone(get_authenticated_user())

    def test_citizen_login_and_logout(self):
        success, msg = login_citizen("citizen@example.com", "citizen123")
        self.assertTrue(success)
        self.assertEqual(get_current_role(), "citizen")
        self.assertTrue(is_citizen_authenticated())
        self.assertFalse(is_municipal_authenticated())
        self.assertEqual(get_authenticated_user(), "citizen@example.com")

        logout()
        self.assertIsNone(get_current_role())
        self.assertFalse(is_citizen_authenticated())

    def test_municipal_invalid_login(self):
        success, msg = login_municipal("wronguser", "wrongpass")
        self.assertFalse(success)
        self.assertFalse(is_municipal_authenticated())
        self.assertIn("Invalid", msg)

    def test_municipal_successful_login_and_logout(self):
        success, msg = login_municipal("officer", "water2026")
        self.assertTrue(success)
        self.assertEqual(get_current_role(), "municipal")
        self.assertTrue(is_municipal_authenticated())
        self.assertFalse(is_citizen_authenticated())
        self.assertEqual(get_authenticated_user(), "officer")

        logout()
        self.assertIsNone(get_current_role())
        self.assertFalse(is_municipal_authenticated())
