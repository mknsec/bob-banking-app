# Banking Web Application — Build Plan

> This is the **agent execution plan**. Each sub-task is self-contained and must be completed
> and verified before the next begins. Status is updated after each sub-task is done.
> Reference documents: `IMPLEMENTATION_PLAN.md` and `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md`.

---

## Top-Level Overview

Build a full-stack banking web application from scratch across two root folders:
- `FRONTEND/` — Jinja2/Bootstrap HTML templates and static assets
- `BACKEND/` — Python Flask application, SQLite database, and tests

The build proceeds in seven sequential sub-tasks that mirror the implementation guide.
Each sub-task is independently reviewable and produces a verifiable outcome.

---

## Sub-Task 1 — Project Scaffolding & Environment

**Status:** `[ ] pending`

**Intent:**
Create the complete folder skeleton and all non-code configuration files so that
every subsequent sub-task has a known, consistent place to put its files.

**Expected Outcomes:**
- `FRONTEND/templates/` directory exists
- `FRONTEND/static/css/` directory exists
- `BACKEND/tests/` directory exists
- `BACKEND/requirements.txt` exists with `flask`, `werkzeug`, `pytest`
- A `.gitignore` exists that excludes `banking.db`, `venv/`, `__pycache__/`, `*.pyc`
- A `README.md` exists at the project root with startup instructions

**Todo List:**
1. Create directory tree: `FRONTEND/templates/`, `FRONTEND/static/css/`, `BACKEND/tests/`
2. Create `BACKEND/requirements.txt` with pinned dependencies: `flask`, `werkzeug`, `pytest`
3. Create `.gitignore` excluding `BACKEND/banking.db`, `venv/`, `.venv/`, `__pycache__/`, `*.pyc`, `.env`
4. Create `README.md` at repo root with local-run instructions referencing the startup steps

**Relevant Context:**
- Folder layout defined in `IMPLEMENTATION_PLAN.md` § 4
- Dependency list from `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` § 1.3

---

## Sub-Task 2 — Database Layer (`database.py`)

**Status:** `[ ] pending`

**Intent:**
Build the entire data access layer before any Flask routes exist, so it can be
tested and seeded independently.

**Expected Outcomes:**
- `BACKEND/database.py` exists and is importable
- Contains: `get_connection()`, `init_db()`, `get_user_by_username()`, `get_balance()`, `update_balance()`
- `init_db()` creates `users` and `accounts` tables if they do not exist
- `init_db()` seeds two demo accounts when the database is empty
- Passwords are stored as Werkzeug `generate_password_hash` hashes
- DB path is resolved from `__file__` so it works regardless of working directory

**Todo List:**
1. Create `BACKEND/database.py`
2. Implement `get_connection()` — opens `banking.db` with `row_factory = sqlite3.Row`; resolves absolute path using `os.path`
3. Implement `init_db()` — creates `users` table (id, username, password_hash) and `accounts` table (id, user_id FK, balance); seeds two demo users (`alice`/`password123`, `bob`/`password123`) with starting balances
4. Implement `get_user_by_username(username)` — returns a single row or `None`
5. Implement `get_balance(user_id)` — returns the float balance for a user
6. Implement `update_balance(user_id, new_balance)` — writes and commits the new balance

**Relevant Context:**
- `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` § 2.2 and § 4.2
- `IMPLEMENTATION_PLAN.md` § 3 (Database Responsibilities)

---

## Sub-Task 3 — Flask Application & Routes (`app.py`)

**Status:** `[ ] pending`

**Intent:**
Create the Flask entry point with all six routes, the `login_required` decorator,
session management, authentication logic, and error handlers.
The app must point Flask at the `FRONTEND/` folder for templates and static files.

**Expected Outcomes:**
- `BACKEND/app.py` exists and is runnable with `flask run`
- Flask is configured with `template_folder=../FRONTEND/templates` and `static_folder=../FRONTEND/static`
- Secret key is set (dev hard-coded string; reads `SECRET_KEY` env var if present)
- `init_db()` is called inside `with app.app_context()` at startup
- Routes defined: `GET /`, `GET+POST /login`, `GET /logout`, `GET /dashboard`, `GET+POST /deposit`, `GET+POST /withdraw`
- `login_required` decorator guards `/dashboard`, `/deposit`, `/withdraw`
- Authentication uses `check_password_hash`; generic error returned for any credential mismatch
- `session.clear()` on logout
- 404 and 500 error handlers registered
- Post/Redirect/Get pattern applied to all successful POST handlers

**Todo List:**
1. Create `BACKEND/app.py`
2. Instantiate Flask with correct `template_folder` and `static_folder` paths (relative to `app.py` location)
3. Set `app.secret_key` from env var `SECRET_KEY`, falling back to a dev default
4. Call `init_db()` inside an `app.app_context()` block at module level
5. Implement `login_required` decorator using `functools.wraps`
6. Implement `GET /` → redirect to `/login`
7. Implement `GET /login` → render `login.html`; redirect to `/dashboard` if already logged in
8. Implement `POST /login` → validate inputs → authenticate → set session → redirect or re-render with error
9. Implement `GET /logout` → `session.clear()` → redirect to `/login`
10. Implement `GET /dashboard` (login_required) → fetch balance → render `dashboard.html`
11. Implement `GET /deposit` (login_required) → render `deposit.html`
12. Implement `POST /deposit` (login_required) → validate amount → update balance → flash success → redirect to `/dashboard`
13. Implement `GET /withdraw` (login_required) → fetch balance → render `withdraw.html`
14. Implement `POST /withdraw` (login_required) → validate amount → check funds → update balance → flash success → redirect to `/dashboard`
15. Register `@app.errorhandler(404)` and `@app.errorhandler(500)` handlers

**Relevant Context:**
- `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` §§ 2.1, 2.3 – 2.7, 4.1 – 4.4, 5.1 – 5.4
- Sub-Task 2 must be complete (database.py importable) before this sub-task

---

## Sub-Task 4 — Frontend Templates

**Status:** `[ ] pending`

**Intent:**
Create all five Jinja2 HTML templates. The templates are purely presentational —
no business logic. Bootstrap is loaded from CDN only.

**Expected Outcomes:**
- `FRONTEND/templates/base.html` — full document skeleton, Bootstrap CDN link, navbar with conditional Logout link, flash messages block, content block
- `FRONTEND/templates/login.html` — extends base, centred card with login form, inline error display
- `FRONTEND/templates/dashboard.html` — extends base, welcome heading, formatted balance, Deposit and Withdraw buttons
- `FRONTEND/templates/deposit.html` — extends base, deposit amount form, Back to Dashboard link
- `FRONTEND/templates/withdraw.html` — extends base, withdraw amount form, current balance display, Back to Dashboard link
- `FRONTEND/static/css/style.css` — minimal overrides only (body background colour, card shadow)

**Todo List:**
1. Create `FRONTEND/templates/base.html` with Bootstrap 5 CDN, navbar (shows "Logout" when `session.user_id` is set), flash messages loop, and `{% block content %}{% endblock %}`
2. Create `FRONTEND/templates/login.html` extending base — Bootstrap card centred with `col-md-4 offset-md-4`, form posts to `/login`, error alert block
3. Create `FRONTEND/templates/dashboard.html` extending base — welcome `<h2>`, balance formatted with `"${:,.2f}".format(balance)` pattern via Jinja2, two `btn` links to `/deposit` and `/withdraw`
4. Create `FRONTEND/templates/deposit.html` extending base — card with amount input (`type="number"`, `min="0.01"`, `step="0.01"`), error display, posts to `/deposit`, back link
5. Create `FRONTEND/templates/withdraw.html` extending base — same as deposit but posts to `/withdraw`, shows current balance as guidance
6. Create `FRONTEND/static/css/style.css` with minimal body and card styles

**Relevant Context:**
- `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` §§ 3.1 – 3.6
- `IMPLEMENTATION_PLAN.md` § 3 (Frontend Responsibilities)
- Sub-Task 3 must be complete so template variable names are known

---

## Sub-Task 5 — Validation Layer

**Status:** `[ ] pending`

**Intent:**
Centralise all input validation into a reusable helper so route handlers stay
clean and validation rules are defined in one place.

**Expected Outcomes:**
- `BACKEND/validators.py` exists with `validate_amount(raw_value)` returning `(float_value, error_message)` — error is `None` on success
- Login field presence checks are inline in `app.py` (simple enough to not warrant a separate module)
- Withdrawal insufficient-funds check remains inline in the withdraw route (it requires the DB balance)
- All validation rules from the guide are covered: empty, non-numeric, zero/negative, precision (2dp)

**Todo List:**
1. Create `BACKEND/validators.py`
2. Implement `validate_amount(raw_value)` — checks: present → numeric → positive → max 2dp → returns `(amount_float, None)` on success or `(None, error_str)` on failure
3. Update the deposit POST handler in `app.py` to call `validate_amount()`
4. Update the withdraw POST handler in `app.py` to call `validate_amount()`

**Relevant Context:**
- `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` §§ 5.2 – 5.4
- Sub-Task 3 must be complete so the route handlers exist to update

---

## Sub-Task 6 — Tests

**Status:** `[ ] pending`

**Intent:**
Write the automated test suite covering unit tests for the validator and database
helpers, plus integration tests for every route using Flask's test client.

**Expected Outcomes:**
- `BACKEND/tests/__init__.py` exists (empty, makes tests a package)
- `BACKEND/tests/test_validators.py` — unit tests for `validate_amount` covering all rules
- `BACKEND/tests/test_database.py` — unit tests for `get_user_by_username`, `get_balance`, `update_balance` using in-memory SQLite
- `BACKEND/tests/test_routes.py` — integration tests for all 10 route scenarios listed in the guide
- All tests pass when running `pytest` from the `BACKEND/` directory

**Todo List:**
1. Create `BACKEND/tests/__init__.py` (empty)
2. Create `BACKEND/tests/test_validators.py` — test empty, non-numeric, zero, negative, valid amounts
3. Create `BACKEND/tests/test_database.py` — pytest fixture that creates in-memory DB; tests for each helper function
4. Create `BACKEND/tests/test_routes.py` — pytest fixture that configures app for testing with in-memory DB; tests for: GET /login, POST /login valid, POST /login invalid, GET /dashboard no session, GET /dashboard with session, POST /deposit valid, POST /deposit invalid, POST /withdraw valid, POST /withdraw insufficient funds, GET /logout
5. Run `pytest` and confirm all tests pass — fix any failures before marking done

**Relevant Context:**
- `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` §§ 6.1 – 6.2
- Sub-Tasks 2, 3, and 5 must be complete before tests can be written

---

## Sub-Task 7 — Final Integration & README

**Status:** `[ ] pending`

**Intent:**
Confirm the entire application runs end-to-end from a clean start, and ensure
the README gives a developer everything they need to run the app locally in
under five minutes.

**Expected Outcomes:**
- Application starts cleanly with `flask run` from `BACKEND/`
- Navigating to `http://127.0.0.1:5000` redirects to the login page
- Login works with seeded credentials (`alice` / `password123`)
- Deposit and withdrawal update the balance correctly
- Logout clears the session
- All tests continue to pass
- `README.md` contains: prerequisites, setup steps (venv + pip install), how to run, how to run tests, seeded demo credentials

**Todo List:**
1. Do a clean end-to-end smoke test: start the app, log in, deposit, withdraw, log out
2. Verify `pytest` still reports all tests passing
3. Update `README.md` with complete, accurate startup instructions including demo credentials
4. Confirm `.gitignore` excludes `banking.db` and `venv/`

**Relevant Context:**
- `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` § 7.1
- All previous sub-tasks must be complete

---

*Agent instructions: process one sub-task at a time using `start_subtask`. After each sub-task, update its Status to `[x] done` in this file and add any notes needed for the next sub-task under a "Notes" bullet before proceeding.*
