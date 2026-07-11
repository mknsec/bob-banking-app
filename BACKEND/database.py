"""
database.py — SQLite data access layer for the Banking application.

Responsibilities:
- Open / close connections to banking.db
- Initialise schema on first run
- Seed demo accounts when the DB is empty
- Provide query helpers used by app.py routes
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# Resolve the absolute path to banking.db relative to this file,
# so the app works regardless of the working directory it is launched from.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banking.db")


def get_connection():
    """
    Open and return a connection to the SQLite database.

    row_factory is set to sqlite3.Row so that query results can be accessed
    by column name (e.g. row['username']) rather than by positional index.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create the schema tables if they do not already exist, then seed
    two demo user accounts if the users table is empty.

    Called once at application startup inside an app_context block.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- Schema -----------------------------------------------------------
    # users: stores login credentials
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL
        )
    """)

    # accounts: stores the balance for each user (one account per user)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            balance REAL    NOT NULL DEFAULT 0.0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()

    # --- Seed data --------------------------------------------------------
    # Only insert demo accounts when the table is completely empty so that
    # re-starting the app does not duplicate or overwrite existing data.
    existing = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing == 0:
        demo_users = [
            ("alice", "password123", 1000.00),
            ("bob",   "password123", 2500.00),
        ]
        for username, password, balance in demo_users:
            hashed = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed),
            )
            user_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO accounts (user_id, balance) VALUES (?, ?)",
                (user_id, balance),
            )
        conn.commit()

    conn.close()


def get_user_by_username(username):
    """
    Return the users row for the given username, or None if not found.

    The returned object behaves like a dict: row['id'], row['username'],
    row['password_hash'].
    """
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return user


def get_balance(user_id):
    """
    Return the current account balance (float) for the given user_id.
    Returns 0.0 if no account row is found (should not happen after init_db).
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT balance FROM accounts WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return float(row["balance"]) if row else 0.0


def update_balance(user_id, new_balance):
    """
    Persist a new balance value for the given user_id.
    The write is committed immediately.
    """
    conn = get_connection()
    conn.execute(
        "UPDATE accounts SET balance = ? WHERE user_id = ?",
        (new_balance, user_id),
    )
    conn.commit()
    conn.close()
