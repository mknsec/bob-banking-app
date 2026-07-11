"""
test_routes.py — Integration tests for all Flask routes.

Uses Flask's built-in test client. Each test starts with a fresh
in-memory-style (tmp_path) database so tests are fully isolated.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import database
import app as app_module
from database import init_db, get_balance, get_user_by_username


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(monkeypatch, tmp_path):
    """
    Configure the Flask app for testing:
    - Redirect DB_PATH to a temporary file (not the real banking.db)
    - Enable TESTING mode (no real errors swallowed)
    - Use a fixed secret key
    Returns a Flask test client.
    """
    db_file = str(tmp_path / "test_banking.db")
    monkeypatch.setattr(database, "DB_PATH", db_file)

    app_module.app.config["TESTING"] = True
    app_module.app.config["SECRET_KEY"] = "test-secret-key"

    with app_module.app.app_context():
        init_db()

    with app_module.app.test_client() as client:
        yield client


@pytest.fixture()
def logged_in_client(client):
    """
    A test client with alice already logged in.
    """
    client.post("/login", data={"username": "alice", "password": "password123"})
    return client


# ---------------------------------------------------------------------------
# Authentication routes
# ---------------------------------------------------------------------------

class TestLoginRoute:

    def test_get_login_returns_200(self, client):
        response = client.get("/login")
        assert response.status_code == 200
        assert b"Customer Login" in response.data

    def test_root_redirects_to_login(self, client):
        response = client.get("/")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_post_valid_credentials_redirects_to_dashboard(self, client):
        response = client.post(
            "/login",
            data={"username": "alice", "password": "password123"},
        )
        assert response.status_code == 302
        assert "/dashboard" in response.headers["Location"]

    def test_post_wrong_password_returns_200_with_error(self, client):
        response = client.post(
            "/login",
            data={"username": "alice", "password": "wrongpassword"},
        )
        assert response.status_code == 200
        assert b"Invalid username or password" in response.data

    def test_post_nonexistent_user_returns_generic_error(self, client):
        response = client.post(
            "/login",
            data={"username": "nobody", "password": "password123"},
        )
        assert response.status_code == 200
        assert b"Invalid username or password" in response.data

    def test_post_blank_username_returns_error(self, client):
        response = client.post(
            "/login",
            data={"username": "", "password": "password123"},
        )
        assert response.status_code == 200
        assert b"required" in response.data.lower()

    def test_post_blank_password_returns_error(self, client):
        response = client.post(
            "/login",
            data={"username": "alice", "password": ""},
        )
        assert response.status_code == 200
        assert b"required" in response.data.lower()


class TestLogoutRoute:

    def test_logout_clears_session_and_redirects(self, logged_in_client):
        response = logged_in_client.get("/logout")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_dashboard_inaccessible_after_logout(self, logged_in_client):
        logged_in_client.get("/logout")
        response = logged_in_client.get("/dashboard")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


# ---------------------------------------------------------------------------
# Protected routes — unauthenticated access
# ---------------------------------------------------------------------------

class TestProtectedRoutesRequireLogin:

    def test_dashboard_redirects_without_session(self, client):
        response = client.get("/dashboard")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_deposit_get_redirects_without_session(self, client):
        response = client.get("/deposit")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_withdraw_get_redirects_without_session(self, client):
        response = client.get("/withdraw")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class TestDashboardRoute:

    def test_dashboard_shows_balance(self, logged_in_client):
        response = logged_in_client.get("/dashboard")
        assert response.status_code == 200
        # Alice starts with $1000.00
        assert b"1000.00" in response.data

    def test_dashboard_shows_username(self, logged_in_client):
        response = logged_in_client.get("/dashboard")
        assert response.status_code == 200
        assert b"Alice" in response.data


# ---------------------------------------------------------------------------
# Deposit
# ---------------------------------------------------------------------------

class TestDepositRoute:

    def test_get_deposit_returns_200(self, logged_in_client):
        response = logged_in_client.get("/deposit")
        assert response.status_code == 200
        assert b"Deposit" in response.data

    def test_valid_deposit_updates_balance_and_redirects(self, logged_in_client):
        response = logged_in_client.post(
            "/deposit", data={"amount": "250.00"}
        )
        assert response.status_code == 302
        assert "/dashboard" in response.headers["Location"]
        # Verify balance in DB
        with app_module.app.app_context():
            user = get_user_by_username("alice")
            balance = get_balance(user["id"])
        assert balance == 1250.00

    def test_deposit_zero_returns_error(self, logged_in_client):
        response = logged_in_client.post("/deposit", data={"amount": "0"})
        assert response.status_code == 200
        assert b"greater than zero" in response.data.lower()

    def test_deposit_negative_returns_error(self, logged_in_client):
        response = logged_in_client.post("/deposit", data={"amount": "-100"})
        assert response.status_code == 200
        assert b"greater than zero" in response.data.lower()

    def test_deposit_non_numeric_returns_error(self, logged_in_client):
        response = logged_in_client.post("/deposit", data={"amount": "abc"})
        assert response.status_code == 200
        assert b"number" in response.data.lower()

    def test_deposit_empty_returns_error(self, logged_in_client):
        response = logged_in_client.post("/deposit", data={"amount": ""})
        assert response.status_code == 200
        assert b"required" in response.data.lower()


# ---------------------------------------------------------------------------
# Withdraw
# ---------------------------------------------------------------------------

class TestWithdrawRoute:

    def test_get_withdraw_returns_200_with_balance(self, logged_in_client):
        response = logged_in_client.get("/withdraw")
        assert response.status_code == 200
        assert b"1000.00" in response.data

    def test_valid_withdrawal_updates_balance_and_redirects(self, logged_in_client):
        response = logged_in_client.post(
            "/withdraw", data={"amount": "100.00"}
        )
        assert response.status_code == 302
        assert "/dashboard" in response.headers["Location"]
        with app_module.app.app_context():
            user = get_user_by_username("alice")
            balance = get_balance(user["id"])
        assert balance == 900.00

    def test_insufficient_funds_returns_error(self, logged_in_client):
        response = logged_in_client.post(
            "/withdraw", data={"amount": "9999.00"}
        )
        assert response.status_code == 200
        assert b"insufficient" in response.data.lower()

    def test_withdraw_exact_balance_succeeds(self, logged_in_client):
        response = logged_in_client.post(
            "/withdraw", data={"amount": "1000.00"}
        )
        assert response.status_code == 302
        with app_module.app.app_context():
            user = get_user_by_username("alice")
            balance = get_balance(user["id"])
        assert balance == 0.00

    def test_withdraw_zero_returns_error(self, logged_in_client):
        response = logged_in_client.post("/withdraw", data={"amount": "0"})
        assert response.status_code == 200
        assert b"greater than zero" in response.data.lower()

    def test_withdraw_empty_returns_error(self, logged_in_client):
        response = logged_in_client.post("/withdraw", data={"amount": ""})
        assert response.status_code == 200
        assert b"required" in response.data.lower()
