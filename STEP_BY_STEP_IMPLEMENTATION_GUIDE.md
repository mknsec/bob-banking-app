# Banking Web Application — Step-by-Step Implementation Guide

> This guide provides plain-English instructions and logic for implementing the Banking Web Application
> described in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).
> It does **not** contain complete source code — it explains *what* to build and *why* each step is needed.

---

## Step 1 — Environment Setup

### 1.1 Prerequisites
Before writing any code, confirm the following tools are available on the machine:
- **Python 3.9 or higher** — the runtime for Flask.
- **pip** — the Python package installer, bundled with Python.
- A terminal / command prompt with access to the project folder.

### 1.2 Create a Virtual Environment
A virtual environment isolates the project's dependencies from other Python projects on the same machine.

- Navigate to the `BACKEND/` folder in the terminal.
- Create a virtual environment using Python's built-in `venv` module. Give it a conventional name like `venv` or `.venv`.
- **Activate** the virtual environment. The activation command differs by OS:
  - On **Windows** the activation script is inside a `Scripts/` sub-folder.
  - On **macOS / Linux** the activation script is inside a `bin/` sub-folder.
- Once activated, every `pip install` command will install packages into this isolated environment only.

### 1.3 Create requirements.txt
Inside `BACKEND/`, create a plain-text file called `requirements.txt`. List one dependency per line:
- `flask` — the web framework that handles routing, sessions, and template rendering.
- `werkzeug` — ships with Flask; provides the password hashing utilities you will use.
- `pytest` — the test runner for unit and integration tests.

Install all dependencies in one step by pointing `pip install` at this file using the `-r` flag.

### 1.4 Verify the Flask Installation
After installing, verify Flask is available by asking the Flask command-line tool for its version.
If a version number is printed, the environment is ready.

### 1.5 Tell Flask Where the Application Lives
Flask needs two environment variables before it can be started:
- `FLASK_APP` — set this to the name of the entry-point file (`app.py`).
- `FLASK_ENV` — set this to `development` during local work so that the server auto-reloads when files change and shows detailed error pages.

On macOS / Linux these are set with `export`; on Windows with `set` or PowerShell's `$env:`.

---

## Step 2 — Backend Implementation

### 2.1 Create the Flask Application Entry Point (`app.py`)
Create `BACKEND/app.py`. This file is the heart of the backend. Its responsibilities are:

1. **Instantiate the Flask app object** — pass `__name__` so Flask knows where to find templates and static files. Also tell Flask to look for templates in `FRONTEND/templates/` and static files in `FRONTEND/static/` by setting the `template_folder` and `static_folder` arguments when creating the app object.
2. **Set a secret key** — Flask's session mechanism requires a secret key to sign cookies. During development any hard-coded string works; in production this must come from an environment variable and never be committed to source control.
3. **Initialise the database** — call the initialisation function from `database.py` so the database tables are created the first time the app starts.
4. **Register all routes** — each URL the browser can visit must map to a Python function.

### 2.2 Create the Database Helper (`database.py`)
Create `BACKEND/database.py`. This module owns everything database-related:

- **`get_connection()`** — opens and returns a connection to the SQLite file (`banking.db`). Set the `row_factory` on the connection so that query results behave like dictionaries (accessible by column name) rather than plain tuples.
- **`init_db()`** — checks whether the required tables exist and creates them if not. It also checks whether any seed users exist and inserts a small set of demo accounts if the database is empty. This function is called once when the app starts.
- **`get_user_by_username(username)`** — queries the users table for a single row matching the given username. Returns `None` if no match is found.
- **`get_balance(user_id)`** — returns the current account balance for the given user ID.
- **`update_balance(user_id, new_balance)`** — writes the new balance value for the given user to the database and commits the transaction.

### 2.3 Define the Routes

Each route is a Python function decorated with `@app.route(...)`. Define the following routes inside `app.py`:

#### `GET /` — Root Redirect
- Logic: Simply redirect the browser to `/login`. This ensures the root URL always leads somewhere meaningful.

#### `GET /login` and `POST /login` — Login Route
- **GET**: Render the login page template. If the user already has an active session, redirect them straight to `/dashboard` instead.
- **POST**: Read the `username` and `password` fields from the submitted form. Pass them to the authentication logic. On success, create a session and redirect to `/dashboard`. On failure, re-render the login page with an error message.

#### `GET /logout` — Logout Route
- Logic: Clear the Flask session entirely, then redirect to `/login`. No template is needed.

#### `GET /dashboard` — Dashboard Route
- Logic: This route is protected — check for an active session first. If there is no session, redirect to `/login`. If the session is valid, look up the current user's balance and pass it to the dashboard template for rendering.

#### `GET /deposit` and `POST /deposit` — Deposit Route
- **GET**: Render the deposit form template. Protected — redirect to login if no session.
- **POST**: Read the submitted `amount` field. Validate it (see Section 5). If valid, add the amount to the current balance, save the new balance, flash a success message, and redirect to `/dashboard`. If invalid, re-render the form with an error message.

#### `GET /withdraw` and `POST /withdraw` — Withdrawal Route
- **GET**: Render the withdrawal form template. Protected — redirect to login if no session.
- **POST**: Read the submitted `amount` field. Validate it (see Section 5). If valid and funds are sufficient, subtract the amount from the balance, save the updated balance, flash a success message, and redirect to `/dashboard`. If funds are insufficient or the amount is invalid, re-render the form with an appropriate error message.

### 2.4 Implement the `login_required` Guard
Rather than repeating the session-check logic in every protected route, extract it into a reusable decorator. The decorator:
1. Checks whether `user_id` (or a similar key) exists in `flask.session`.
2. If the key is absent, redirects to `/login` immediately.
3. If the key is present, calls the original route function and returns its response.

Apply this decorator to the dashboard, deposit, and withdraw routes.

### 2.5 Implement Authentication Logic
The login POST handler needs to authenticate the user. The logic flow is:
1. Retrieve the user record from the database by username.
2. If no record is found, the username is wrong — return a generic error ("Invalid username or password"). Never reveal which field was wrong.
3. If a record is found, use Werkzeug's `check_password_hash` function to compare the submitted password against the stored hash.
4. If the hash does not match, return the same generic error.
5. If the hash matches, store the user's ID (and optionally their username for display) in `flask.session` and redirect to `/dashboard`.

### 2.6 Session Management
Flask's session is a signed cookie stored in the browser. Key points:
- Store only the minimum necessary information — the `user_id` is sufficient.
- The session is automatically available in every route via `flask.session`.
- Clearing the session on logout is done with `session.clear()`.
- Set `session.permanent = False` (the default) so the session expires when the browser is closed.

### 2.7 Error Handling
Add two simple error handlers to `app.py`:
- **404 handler** — when a user navigates to a URL that does not exist, render a simple "Page not found" message.
- **500 handler** — when an unexpected server error occurs, render a simple "Something went wrong" message rather than exposing a raw Python traceback to the user.

These are registered using Flask's `@app.errorhandler(code)` decorator.

---

## Step 3 — Frontend Implementation

All HTML files live in `FRONTEND/templates/`. Flask will automatically find them there because of the `template_folder` setting in `app.py`. Every template uses Jinja2 syntax to receive data from Python and render it dynamically.

### 3.1 Create the Base Layout (`base.html`)
This is the shared skeleton that all other pages extend. It should contain:
- The full HTML document structure (`<html>`, `<head>`, `<body>`).
- A `<meta charset>` tag and a viewport meta tag for responsive behaviour.
- A `<link>` tag pointing to the Bootstrap CSS CDN — this is the only styling dependency.
- A **navbar** component (Bootstrap's `navbar`) that shows the application name. When a user is logged in, show a "Logout" link in the navbar; otherwise show nothing or a "Login" link.
- A **flash messages block** — loop over Flask's `get_flashed_messages(with_categories=True)` and render each message inside a Bootstrap `alert` component with the appropriate colour (green for success, red for danger/error).
- A **content block** (`{% block content %}{% endblock %}`) where each child template injects its page-specific HTML.

### 3.2 Create the Login Page (`login.html`)
This page extends `base.html` and fills the content block with:
- A centred Bootstrap `card` component containing the login form.
- Two input fields: one for `username` (type `text`) and one for `password` (type `password`). Both must have `name` attributes that match what the Flask route reads from `request.form`.
- A submit button labelled "Log In".
- The form's `action` must point to `/login` and the `method` must be `POST`.
- If the route passes an error message variable to the template, display it above the form inside a Bootstrap `alert alert-danger` block.

### 3.3 Create the Dashboard (`dashboard.html`)
This page extends `base.html` and shows:
- A welcome heading that includes the logged-in user's name (passed as a template variable from the route).
- The current account balance displayed prominently — format it as currency (e.g. two decimal places).
- Two Bootstrap buttons linking to the deposit and withdraw pages.
- The logout link is already handled by the navbar in `base.html`.

### 3.4 Create the Deposit Form (`deposit.html`)
This page extends `base.html` and contains:
- A centred card with a heading "Deposit Funds".
- A single numeric input field for the amount. Set `min="0.01"` and `step="0.01"` as HTML attributes to guide the browser — but remember that server-side validation (Section 5) is the real guard.
- A submit button labelled "Deposit".
- The form posts to `/deposit`.
- A "Back to Dashboard" link below the form.

### 3.5 Create the Withdrawal Form (`withdraw.html`)
This page extends `base.html` and contains:
- A centred card with a heading "Withdraw Funds".
- A single numeric input field for the amount, same attributes as the deposit form.
- A submit button labelled "Withdraw".
- The form posts to `/withdraw`.
- The current balance can optionally be displayed on this page to help the user know their limit — pass it from the route.
- A "Back to Dashboard" link below the form.

### 3.6 Bootstrap Layout Principles
- Use Bootstrap's **grid system** (`container`, `row`, `col`) to centre forms on the page.
- Use Bootstrap's **card** component to give forms a clean, boxed appearance.
- Use Bootstrap's **btn** classes for all buttons.
- Use Bootstrap's **alert** classes for flash messages and inline errors.
- Do not write custom CSS unless there is a specific visual requirement not covered by Bootstrap utilities.

---

## Step 4 — Integration Steps

### 4.1 Connect Flask to the Frontend Templates
Flask needs to know where the templates and static files are. When creating the Flask app object in `app.py`, set:
- `template_folder` to the path `../FRONTEND/templates` (relative to `BACKEND/app.py`).
- `static_folder` to the path `../FRONTEND/static` (relative to `BACKEND/app.py`).

Once this is done, every call to `render_template('login.html', ...)` in a route will find the correct file automatically.

### 4.2 Connect Flask to SQLite
The connection is made inside `database.py`:
- The path to `banking.db` should be expressed relative to the location of `database.py` itself, using Python's `__file__` variable to build an absolute path. This ensures the app works regardless of which directory it is launched from.
- Each request that needs the database should open a fresh connection and close it when done. Flask's `teardown_appcontext` hook can be used to close the connection automatically at the end of each request.
- The `init_db()` function in `database.py` is called once at startup by `app.py` using Flask's `with app.app_context()` block to ensure the database and tables exist before the first request arrives.

### 4.3 Passing Data from Route to Template
Every route that renders a template passes data as keyword arguments to `render_template`. For example:
- The dashboard route reads the balance from the database and passes it as `balance=...`.
- The login route passes `error=None` by default, and `error="Invalid username or password"` on a failed login attempt.
- The withdraw route can pass `balance=...` so the form can display the current balance.

Inside the Jinja2 template, these variables are accessed with double curly braces: `{{ balance }}`.

### 4.4 Handling Form Submissions
When a form is submitted, the browser sends a POST request and Flask reads the values with `request.form.get('field_name')`. Key points:
- Always use `.get()` rather than direct dictionary access — it returns `None` instead of raising a `KeyError` if the field is missing.
- After a successful POST action (deposit, withdraw, login), always **redirect** the user rather than rendering a template directly. This is the **Post/Redirect/Get (PRG)** pattern and prevents the browser from re-submitting the form if the user refreshes the page.

---

## Step 5 — Validation Rules

All validation logic lives in the Flask route handlers in `app.py`. The frontend HTML attributes (`min`, `step`, `required`) provide a convenience hint but are not a security control — they can be bypassed.

### 5.1 Login Validation
| Check | Rule | Action on Failure |
|---|---|---|
| Username not empty | The submitted username must not be blank | Re-render login with "Username is required" |
| Password not empty | The submitted password must not be blank | Re-render login with "Password is required" |
| Username exists | A user with that username must exist in the database | Re-render login with generic error |
| Password matches | Hashed password in DB must match submitted value | Re-render login with generic error |

> **Security note:** Always return the same generic message ("Invalid username or password") for both a missing user and a wrong password. Separate messages reveal which field is wrong and help attackers enumerate valid usernames.

### 5.2 Deposit Validation
| Check | Rule | Action on Failure |
|---|---|---|
| Amount present | The amount field must not be empty | Re-render deposit form with "Amount is required" |
| Amount is numeric | The value must be convertible to a number | Re-render deposit form with "Amount must be a number" |
| Amount is positive | The value must be greater than zero | Re-render deposit form with "Amount must be greater than zero" |
| Amount has valid precision | Optionally: no more than 2 decimal places | Re-render deposit form with "Amount must have at most 2 decimal places" |

If all checks pass, add the amount to the current balance and save.

### 5.3 Withdrawal Validation
| Check | Rule | Action on Failure |
|---|---|---|
| Amount present | The amount field must not be empty | Re-render withdraw form with "Amount is required" |
| Amount is numeric | The value must be convertible to a number | Re-render withdraw form with "Amount must be a number" |
| Amount is positive | The value must be greater than zero | Re-render withdraw form with "Amount must be greater than zero" |
| Sufficient funds | The current balance minus the amount must be ≥ 0 | Re-render withdraw form with "Insufficient funds" |

If all checks pass, subtract the amount from the balance and save.

### 5.4 General Validation Pattern
Follow this consistent approach in every POST handler:
1. Extract the value from `request.form`.
2. Check for empty / missing input first.
3. Attempt type conversion (e.g. `float(amount)`) inside a `try/except` block to catch non-numeric values.
4. Apply business rule checks in order.
5. If any check fails, immediately re-render the form with the error — do not continue.
6. Only if every check passes, proceed to the database operation and then redirect.

---

## Step 6 — Testing

### 6.1 Unit Tests
Unit tests verify individual pieces of logic in isolation, without starting a real server or touching the real database.

**What to test:**
- The validation helper logic — given a specific amount input, does it correctly pass or fail each rule?
- The `get_user_by_username` and `get_balance` database helpers — using an in-memory SQLite database (`:memory:`) as a fixture so tests do not touch the real `banking.db`.
- Password hashing and checking — verify that a hashed password can be verified and that an incorrect password is rejected.

**How to set up:**
- Create `BACKEND/tests/test_app.py`.
- Import `pytest` and the relevant modules from `app.py` and `database.py`.
- Use pytest **fixtures** to create a fresh, isolated database connection before each test and tear it down afterwards.
- Use `assert` statements to verify outcomes.

### 6.2 Integration Tests
Integration tests verify that routes behave correctly end-to-end — form submission, session state, redirects, and rendered content.

**How Flask enables this:**
Flask provides a built-in **test client** (`app.test_client()`) that simulates HTTP requests without starting a real server. Configure the app for testing by setting `TESTING = True` and pointing it at an in-memory database.

**What to test:**
- `GET /login` returns a 200 status and the login page is rendered.
- `POST /login` with valid credentials redirects to `/dashboard` (302) and sets a session.
- `POST /login` with invalid credentials returns 200 and shows an error message.
- `GET /dashboard` without a session redirects to `/login` (302).
- `GET /dashboard` with a valid session returns 200 and shows the balance.
- `POST /deposit` with a valid amount updates the balance and redirects to `/dashboard`.
- `POST /deposit` with a negative amount re-renders the form with an error.
- `POST /withdraw` with a valid amount and sufficient funds updates the balance.
- `POST /withdraw` with an amount exceeding the balance shows "Insufficient funds".
- `GET /logout` clears the session and redirects to `/login`.

### 6.3 Manual Testing Checklist
Use this checklist to verify the running application in the browser before each demo:

**Authentication**
- [ ] Navigating to `http://localhost:5000` redirects to the login page.
- [ ] Submitting the login form with a blank username shows a validation error.
- [ ] Submitting the login form with an incorrect password shows "Invalid username or password".
- [ ] Submitting the login form with correct credentials lands on the dashboard.
- [ ] Clicking Logout returns to the login page and clears the session (going back in the browser should not restore the dashboard).

**Dashboard**
- [ ] The dashboard shows the correct username and current balance.
- [ ] Deposit and Withdraw buttons are visible and navigate to the correct pages.

**Deposit**
- [ ] Submitting the deposit form with a blank amount shows a validation error.
- [ ] Submitting the deposit form with a zero or negative amount shows a validation error.
- [ ] Submitting a valid deposit amount increases the balance on the dashboard.
- [ ] A success message is displayed on the dashboard after a successful deposit.

**Withdrawal**
- [ ] Submitting the withdraw form with a blank amount shows a validation error.
- [ ] Submitting an amount greater than the current balance shows "Insufficient funds".
- [ ] Submitting a valid withdrawal amount decreases the balance on the dashboard.
- [ ] A success message is displayed after a successful withdrawal.

**Edge Cases**
- [ ] Entering a non-numeric value in the amount field shows a validation error.
- [ ] Directly navigating to `/dashboard` in a fresh browser tab (no session) redirects to login.

---

## Step 7 — Deployment

### 7.1 Running Locally
To start the application on a local machine:

1. Open a terminal and navigate to the `BACKEND/` folder.
2. Activate the virtual environment (see Step 1.2).
3. Ensure environment variables `FLASK_APP=app.py` and `FLASK_ENV=development` are set.
4. Run `flask run`.
5. Flask will print the local URL (typically `http://127.0.0.1:5000`). Open this in a browser.
6. The database file (`banking.db`) is created automatically on first run — no manual setup needed.

To run the test suite: navigate to the `BACKEND/` folder with the virtual environment active and run `pytest`. Pytest will discover all files named `test_*.py` inside the `tests/` folder.

### 7.2 Production Considerations

The development server (`flask run`) is **not suitable for production**. The following considerations apply if this application is ever deployed beyond a local demo:

| Concern | Development Approach | Production Recommendation |
|---|---|---|
| **Web server** | Flask's built-in dev server | Use a production WSGI server such as Gunicorn |
| **Secret key** | Hard-coded string in `app.py` | Read from an environment variable; never commit to source control |
| **Database** | SQLite file on disk | Consider PostgreSQL or MySQL for concurrent users |
| **HTTPS** | Plain HTTP on localhost | Serve behind a reverse proxy (nginx) with TLS certificates |
| **Debug mode** | `FLASK_ENV=development` | Set `FLASK_ENV=production`; never expose debug mode publicly |
| **Password storage** | Werkzeug hashing (acceptable) | Same approach is acceptable; ensure a strong hashing algorithm (bcrypt) |
| **Session security** | Signed cookie | Consider server-side sessions for sensitive applications |
| **Error pages** | Basic 404/500 handlers | Same approach; ensure no stack traces are ever shown to users |
| **Static files** | Served by Flask | Serve directly by nginx for better performance |

### 7.3 GitHub Actions CI (Already Configured)
The repository already contains `banking-app-ci.yml` in `docs/demo-setup/`. This workflow:
- Triggers on every push to the repository.
- Sets up Python 3.11.
- Installs dependencies from `requirements.txt`.
- Runs the test suite with `pytest`.

Once the backend tests are in place and passing locally, this CI pipeline will automatically verify every future code change.

---

*This document provides implementation guidance only. For architecture and scope decisions, refer to [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).*
