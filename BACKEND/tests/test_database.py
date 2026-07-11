"""
test_database.py — Unit tests for BACKEND/database.py

All tests use a temporary on-disk SQLite database via a pytest fixture
so the real banking.db is never touched.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import database
from database import get_user_by_username, get_balance, update_balance, init_db
from werkzeug.security import check_password_hash


@pytest.fixture()
def tmp_db(monkeypatch, tmp_path):
    """
    Redirect DB_PATH to a fresh temporary database for each test,
    then call init_db() to create the schema and seed data.
    """
    db_file = str(tmp_path / "test_banking.db")
    monkeypatch.setattr(database, "DB_PATH", db_file)
    init_db()
    yield db_file


class TestInitDb:
    """Verify that init_db creates schema and seeds demo users."""

    def test_users_table_is_created(self, tmp_db):
        conn = database.get_connection()
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        ).fetchall()
        conn.close()
        assert len(rows) == 1

    def test_accounts_table_is_created(self, tmp_db):
        conn = database.get_connection()
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='accounts'"
        ).fetchall()
        conn.close()
        assert len(rows) == 1

    def test_seed_creates_two_users(self, tmp_db):
        conn = database.get_connection()
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        conn.close()
        assert count == 2

    def test_seed_passwords_are_hashed(self, tmp_db):
        conn = database.get_connection()
        row = conn.execute("SELECT password_hash FROM users WHERE username = 'alice'").fetchone()
        conn.close()
        assert row is not None
        # Hashed value should not be the plain-text password
        assert row["password_hash"] != "password123"
        assert check_password_hash(row["password_hash"], "password123")

    def test_init_db_is_idempotent(self, tmp_db):
        """Calling init_db() a second time must not duplicate seed data."""
        init_db()
        conn = database.get_connection()
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        conn.close()
        assert count == 2


class TestGetUserByUsername:
    def test_returns_user_for_valid_username(self, tmp_db):
        user = get_user_by_username("alice")
        assert user is not None
        assert user["username"] == "alice"

    def test_returns_none_for_missing_username(self, tmp_db):
        user = get_user_by_username("nobody")
        assert user is None

    def test_is_case_sensitive(self, tmp_db):
        user = get_user_by_username("Alice")
        assert user is None


class TestGetBalance:
    def test_alice_has_correct_starting_balance(self, tmp_db):
        user = get_user_by_username("alice")
        balance = get_balance(user["id"])
        assert balance == 1000.00

    def test_bob_has_correct_starting_balance(self, tmp_db):
        user = get_user_by_username("bob")
        balance = get_balance(user["id"])
        assert balance == 2500.00

    def test_returns_zero_for_unknown_user_id(self, tmp_db):
        balance = get_balance(9999)
        assert balance == 0.0


class TestUpdateBalance:
    def test_balance_is_updated_correctly(self, tmp_db):
        user = get_user_by_username("alice")
        update_balance(user["id"], 1500.00)
        assert get_balance(user["id"]) == 1500.00

    def test_balance_can_be_set_to_zero(self, tmp_db):
        user = get_user_by_username("alice")
        update_balance(user["id"], 0.0)
        assert get_balance(user["id"]) == 0.0

    def test_update_persists_across_connections(self, tmp_db):
        """Write via one connection and verify via another."""
        user = get_user_by_username("bob")
        update_balance(user["id"], 999.99)
        fresh_balance = get_balance(user["id"])
        assert fresh_balance == 999.99
