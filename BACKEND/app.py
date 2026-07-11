"""
app.py — Flask application entry point for the Banking Web Application.

Responsibilities:
- Create and configure the Flask app object
- Register all URL routes
- Manage user sessions (login / logout)
- Enforce authentication via the login_required decorator
- Delegate validation to validators.py
- Delegate database access to database.py
- Render Jinja2 templates from FRONTEND/templates/
"""

import os
import functools

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from werkzeug.security import check_password_hash

from database import get_balance, get_user_by_username, init_db, update_balance
from validators import validate_amount

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

# Resolve absolute paths to the FRONTEND folder so Flask finds templates and
# static files regardless of which directory the app is launched from.
_base_dir = os.path.dirname(os.path.abspath(__file__))
_frontend_templates = os.path.join(_base_dir, "..", "FRONTEND", "templates")
_frontend_static = os.path.join(_base_dir, "..", "FRONTEND", "static")

app = Flask(
    __name__,
    template_folder=_frontend_templates,
    static_folder=_frontend_static,
)

# Secret key — read from environment variable in production;
# falls back to a dev-only default that must never be used in production.
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Initialise database schema and seed data on startup.
with app.app_context():
    init_db()


# ---------------------------------------------------------------------------
# Authentication decorator
# ---------------------------------------------------------------------------

def login_required(view_func):
    """
    Decorator that redirects unauthenticated requests to /login.
    Apply to any route that requires the user to be logged in.
    """
    @functools.wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Root URL — always redirect to login."""
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  — Show the login form. Redirect to dashboard if already logged in.
    POST — Validate credentials; create session on success or show error.
    """
    # Already authenticated — skip the login page.
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # --- Field-presence validation ------------------------------------
        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        else:
            # --- Credential validation ------------------------------------
            user = get_user_by_username(username)
            # Generic message for both "user not found" and "wrong password"
            # to prevent username enumeration attacks.
            if user is None or not check_password_hash(user["password_hash"], password):
                error = "Invalid username or password."
            else:
                # Success — store minimal identity in the session.
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect(url_for("dashboard"))

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    """Terminate the session and return to the login page."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    """
    Show the authenticated customer's current balance and navigation actions.
    """
    balance = get_balance(session["user_id"])
    return render_template(
        "dashboard.html",
        username=session["username"],
        balance=balance,
    )


@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    """
    GET  — Show the deposit form.
    POST — Validate amount, credit balance, redirect to dashboard.
    """
    error = None

    if request.method == "POST":
        raw_amount = request.form.get("amount")
        amount, error = validate_amount(raw_amount)

        if error is None:
            current_balance = get_balance(session["user_id"])
            new_balance = round(current_balance + amount, 2)
            update_balance(session["user_id"], new_balance)
            flash(f"Successfully deposited ${amount:,.2f}. New balance: ${new_balance:,.2f}", "success")
            return redirect(url_for("dashboard"))

    return render_template("deposit.html", error=error)


@app.route("/withdraw", methods=["GET", "POST"])
@login_required
def withdraw():
    """
    GET  — Show the withdrawal form with current balance for reference.
    POST — Validate amount, check funds, debit balance, redirect to dashboard.
    """
    current_balance = get_balance(session["user_id"])
    error = None

    if request.method == "POST":
        raw_amount = request.form.get("amount")
        amount, error = validate_amount(raw_amount)

        if error is None:
            if amount > current_balance:
                error = f"Insufficient funds. Your current balance is ${current_balance:,.2f}."
            else:
                new_balance = round(current_balance - amount, 2)
                update_balance(session["user_id"], new_balance)
                flash(f"Successfully withdrew ${amount:,.2f}. New balance: ${new_balance:,.2f}", "success")
                return redirect(url_for("dashboard"))

    return render_template("withdraw.html", error=error, balance=current_balance)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
