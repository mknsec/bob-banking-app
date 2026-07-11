# Banking Web Application

A full-stack banking web application built with **Python Flask**, **SQLite**, and **Bootstrap 5**.

---

## Features

- Customer login with hashed-password authentication
- Dashboard showing current account balance
- Deposit funds
- Withdraw funds (with insufficient-funds guard)
- Secure logout

---

## Project Structure

```
banking-workshop/
├── FRONTEND/
│   ├── templates/          # Jinja2 HTML templates
│   └── static/css/         # Custom CSS overrides
└── BACKEND/
    ├── app.py              # Flask entry point & all routes
    ├── database.py         # SQLite helpers & seed data
    ├── validators.py       # Input validation helpers
    ├── requirements.txt    # Python dependencies
    └── tests/              # Pytest unit & integration tests
```

---

## Prerequisites

- Python 3.9 or higher
- pip (bundled with Python)

---

## Local Setup

### 1. Create and activate a virtual environment

```bash
cd BACKEND
python3 -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the application

```bash
# From the BACKEND/ directory, with the virtual environment active
FLASK_APP=app.py FLASK_ENV=development flask run
# Windows (Command Prompt)
set FLASK_APP=app.py && set FLASK_ENV=development && flask run
```

The application starts at **http://127.0.0.1:5000**

The SQLite database (`banking.db`) is created automatically on first run — no manual setup needed.

---

## Demo Credentials

| Username | Password    | Starting Balance |
|----------|-------------|-----------------|
| alice    | password123 | $1,000.00        |
| bob      | password123 | $2,500.00        |

---

## Running the Tests

```bash
# From the BACKEND/ directory with the virtual environment active
pytest
```

All tests run against an in-memory SQLite database — the real `banking.db` is never touched.

---

## Security Notes

- Passwords are stored using Werkzeug's `generate_password_hash` (PBKDF2-HMAC-SHA256).
- All protected routes require an active session (enforced via a `login_required` decorator).
- The `SECRET_KEY` is read from the `SECRET_KEY` environment variable in production.
- Never run with `FLASK_ENV=development` or `debug=True` in production.
