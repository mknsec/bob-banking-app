# Banking Web Application — Implementation Plan

---

## 1. Solution Overview

### Objective
Build a browser-based banking web application that allows customers to securely log in, view their account balance, deposit funds, withdraw funds, and log out — all through a clean, responsive interface.

### Scope
| In Scope | Out of Scope |
|---|---|
| Customer authentication (login / logout) | Admin portal or bank-staff features |
| Single-account balance view | Multi-account or joint accounts |
| Deposit and withdrawal transactions | Transfers between accounts |
| Session management | Password reset / account creation UI |
| SQLite persistence for demo purposes | Production-grade database (PostgreSQL, MySQL) |
| Responsive UI via Bootstrap | Native mobile application |

### Users
| User Type | Description |
|---|---|
| **Customer** | An authenticated bank customer who interacts with their own account |

### Functional Requirements
1. A customer must be able to log in with a username and password.
2. A customer must be able to view their current account balance on a dashboard.
3. A customer must be able to deposit a positive monetary amount into their account.
4. A customer must be able to withdraw a positive monetary amount, subject to sufficient balance.
5. A customer must be able to log out and have their session terminated.
6. Unauthenticated users must be redirected to the login page.

### Non-Functional Requirements
- **Security** — Passwords must be stored hashed; sessions must be server-managed.
- **Usability** — All pages must be responsive and render correctly on desktop browsers.
- **Reliability** — Invalid or insufficient-fund transactions must be rejected with a clear error message.
- **Portability** — The application must run locally with a single `flask run` command and no external services.
- **Maintainability** — Frontend and backend concerns must be separated into distinct folders.

### Assumptions
- A small set of pre-seeded customer accounts will be available for demo purposes.
- No real payment gateway integration is required.
- A single SQLite database file is sufficient for local development and demos.
- The application will run on `localhost` during the demo.
- Bootstrap is loaded from a CDN; no frontend build toolchain (Webpack, Vite) is needed.

---

## 2. High-Level Architecture

```
┌──────────────────────────────────────────────────────┐
│                     BROWSER                          │
│  HTML pages styled with Bootstrap                    │
│  Forms submit data via HTTP POST                     │
│  Links navigate via HTTP GET                         │
└───────────────┬──────────────────────────────────────┘
                │  HTTP (port 5000)
                ▼
┌──────────────────────────────────────────────────────┐
│                 BACKEND  (Flask)                     │
│  Route handlers for each feature                     │
│  Session management (Flask session / cookie)         │
│  Business logic: balance check, deposit, withdraw    │
│  Jinja2 template rendering                           │
└───────────────┬──────────────────────────────────────┘
                │  SQLite Python driver (sqlite3)
                ▼
┌──────────────────────────────────────────────────────┐
│               DATABASE  (SQLite)                     │
│  Single .db file inside the BACKEND folder           │
│  Stores users and account balances                   │
└──────────────────────────────────────────────────────┘
```

### Frontend → Backend → Database Interaction
- The browser sends an **HTTP request** (GET or POST form submission) to a Flask route.
- Flask **validates** the request, checks the session, applies business rules, and queries or writes to SQLite.
- Flask **renders** a Jinja2 HTML template and sends the response back to the browser.

### Request Lifecycle
```
Browser Request
      │
      ▼
Flask Route Handler
      │
      ├─► Session / Auth check ─► redirect to /login if unauthenticated
      │
      ├─► Business logic (deposit / withdraw validation)
      │
      ├─► SQLite read / write
      │
      └─► Render Jinja2 template ─► HTTP Response ─► Browser renders page
```

---

## 3. Component Design

### Frontend Responsibilities
- Render login, dashboard, deposit, and withdrawal pages.
- Display flash messages (success / error feedback) returned by the backend.
- Send form data to the backend via HTTP POST.
- Bootstrap grid and components provide responsive layout without custom CSS frameworks.
- No client-side business logic — the frontend is purely presentational.

### Backend Responsibilities
- Expose URL routes for every user action: login, logout, dashboard, deposit, withdraw.
- Authenticate users and manage session state.
- Enforce business rules:
  - Reject negative or zero transaction amounts.
  - Reject withdrawals that would result in a negative balance.
- Read and write account data to SQLite via Python's built-in `sqlite3` module.
- Serve rendered HTML pages using Jinja2 templates stored in the FRONTEND folder.

### Database Responsibilities
- Persist user credentials (username + hashed password).
- Persist account balances linked to each user.
- The SQLite file lives inside the BACKEND folder and is created on first run.
- No external database server is required.

---

## 4. Folder Structure

```
banking-workshop/
├── IMPLEMENTATION_PLAN.md          ← This document
├── FRONTEND/
│   ├── templates/                  ← Jinja2 HTML templates rendered by Flask
│   │   ├── base.html               ← Shared layout (navbar, Bootstrap CDN link)
│   │   ├── login.html              ← Login form
│   │   ├── dashboard.html          ← Balance overview and navigation
│   │   ├── deposit.html            ← Deposit form
│   │   └── withdraw.html           ← Withdrawal form
│   └── static/                     ← Static assets served directly by Flask
│       └── css/
│           └── style.css           ← Minimal custom styles (optional overrides)
└── BACKEND/
    ├── app.py                      ← Flask application entry point; all routes
    ├── database.py                 ← DB initialisation and helper functions
    ├── banking.db                  ← SQLite database file (auto-created at runtime)
    ├── requirements.txt            ← Python dependencies (flask, etc.)
    └── tests/
        └── test_app.py             ← Basic unit / integration tests
```

### Folder Responsibilities

| Path | Purpose |
|---|---|
| `FRONTEND/templates/` | HTML templates rendered server-side by Flask via Jinja2 |
| `FRONTEND/static/` | CSS and any static assets served at `/static/` |
| `BACKEND/app.py` | Route definitions, session handling, request processing |
| `BACKEND/database.py` | DB connection, schema initialisation, seed data, query helpers |
| `BACKEND/banking.db` | SQLite data file — NOT committed to version control |
| `BACKEND/requirements.txt` | Pinned Python package versions for reproducible installs |
| `BACKEND/tests/` | Automated tests for routes and business logic |

---

## 5. Module Breakdown

### Authentication Module
**Goal:** Verify customer identity and protect all other routes.

| Concern | Detail |
|---|---|
| Login page | Displays a username/password form |
| Credential validation | Checks submitted credentials against the hashed password in the DB |
| Session creation | Stores the authenticated user ID in the Flask session on success |
| Login failure | Re-renders the login page with an error message |
| Route guard | A helper (e.g. `login_required` decorator) redirects unauthenticated requests |
| Logout | Clears the Flask session and redirects to the login page |

### Dashboard Module
**Goal:** Provide the authenticated customer with a summary of their account and navigation.

| Concern | Detail |
|---|---|
| Balance display | Reads the current balance for the logged-in user and renders it |
| Navigation | Links to Deposit, Withdraw, and Logout actions |
| Access control | Protected by the `login_required` guard |

### Account Management Module
**Goal:** Maintain accurate account balance records.

| Concern | Detail |
|---|---|
| Balance read | Fetch current balance for a user ID from the database |
| Balance update | Write a new balance back to the database after a validated transaction |
| Data integrity | Only committed after all validation passes; no partial writes |

### Transactions Module
**Goal:** Process deposit and withdrawal operations with appropriate validation.

| Concern | Detail |
|---|---|
| Deposit | Accepts a positive amount, adds it to the balance, redirects to dashboard |
| Withdrawal | Accepts a positive amount, checks sufficient funds, deducts from balance |
| Input validation | Rejects non-numeric, zero, or negative amounts before any DB interaction |
| Insufficient funds | Returns an error message without modifying the balance |
| Feedback | Flash messages communicate success or failure back to the user |

---

## 6. Implementation Roadmap

### Phase Overview

| Phase | Focus | Key Deliverables |
|---|---|---|
| **Phase 1** | Project Scaffolding | Folder structure, `requirements.txt`, Flask app skeleton, DB init script |
| **Phase 2** | Authentication | Login page, route, session management, `login_required` guard, logout |
| **Phase 3** | Dashboard | Dashboard route and template showing balance |
| **Phase 4** | Transactions | Deposit and withdraw routes, validation logic, form templates |
| **Phase 5** | Polish & Testing | Flash messages, error states, base layout, automated tests |
| **Phase 6** | CI Integration | GitHub Actions workflow wired to run tests on push |

### Phase Dependencies

```
Phase 1 (Scaffolding)
      │
      └─► Phase 2 (Auth) ─► Phase 3 (Dashboard) ─► Phase 4 (Transactions)
                                                           │
                                                           └─► Phase 5 (Polish & Testing)
                                                                       │
                                                                       └─► Phase 6 (CI)
```

### Estimated Effort

| Phase | Relative Effort |
|---|---|
| Phase 1 — Scaffolding | Low |
| Phase 2 — Authentication | Medium |
| Phase 3 — Dashboard | Low |
| Phase 4 — Transactions | Medium |
| Phase 5 — Polish & Testing | Medium |
| Phase 6 — CI Integration | Low |

### Key Dependencies
- Flask and its Jinja2 templating engine must be installed before any backend work begins.
- The database initialisation script must run successfully before authentication can be tested.
- Authentication (Phase 2) must be complete before Dashboard or Transactions can be verified end-to-end.
- Tests (Phase 5) depend on all application routes being in place.
- CI (Phase 6) depends on a passing local test suite.

---

*This document is a planning artifact. It does not include database schemas, SQL scripts, API contracts, or implementation code.*
