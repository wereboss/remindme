# Notes & Reminders PWA (MVP 1)

A lightweight, responsive Progressive Web Application (PWA) for managing personal notes and visual reminders, powered by Python (Flask) and SQLite.

---

## Current Architecture & Baseline (MVP 1)

* **Backend:** Python 3 + Flask application factory pattern (`app/`)
* **Database:** Embedded SQLite (`notes.sqlite`), with automatic schema creation and foreign key constraints enabled.
* **Security & Multi-Tenancy:**
  * Open self-registration and credential-based login.
  * Passwords hashed via PBKDF2 (`werkzeug.security`).
  * Session-based authentication using HTTP-only cookies.
  * Strict per-user data isolation: every note is bound to `user_id`.
* **Data Model:** Unified `Note` model where setting an optional ISO-8601 `deadline` transforms a note into a visual reminder.
* **Visual Reminders:**
  * ⚠️ **Overdue** (Red badge): deadline has passed.
  * 🔔 **Due Today** (Orange badge): deadline is due today / within 24 hours.
  * 📅 **Upcoming** (Blue badge): future deadline.
  * ✓ **Completed** (Green badge / strikethrough): toggled complete.
* **PWA Tier 1 Shell:**
  * Web App Manifest (`/static/manifest.json`) with standalone display mode.
  * Service Worker (`/sw.js`) precaching static UI assets for offline shell loading and fast app startup.
  * Mobile and desktop responsive layout.

---

## Project Structure

```
├── app/
│   ├── __init__.py          # Flask app factory, blueprint registration & PWA routing
│   ├── auth.py              # Authentication endpoints & login_required decorator
│   ├── db.py                # SQLite connection lifecycle & schema setup
│   ├── notes.py             # Notes CRUD & visual reminder status calculation
│   ├── static/
│   │   ├── css/style.css    # Responsive styles and color-coded reminder badges
│   │   ├── icons/icon.svg   # Scalable PWA vector icon
│   │   ├── js/app.js        # Vanilla JS single-page app logic & Service Worker registration
│   │   ├── manifest.json    # PWA Web App Manifest
│   │   └── sw.js            # Service Worker caching strategy
│   └── templates/
│       └── index.html       # HTML5 PWA shell
├── run.py                   # Server startup script
├── requirements.txt         # Project dependencies (Flask, pytest)
├── spec.md                  # MVP 1 functional specification
├── FAQ.md                   # Troubleshooting, test guide, and MVP 1 limitations
└── README.md                # Project documentation
```

---

## Setup & Running Locally

### 1. Prerequisites
* Python 3.10+ and pip

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python3 run.py
```
By default, the server listens at `http://localhost:5000`.

### 4. PWA Installation
* Open `http://localhost:5000` in Chrome, Chromium, or Safari (iOS).
* In Chrome / Android: Click the **Install** icon in the address bar or select **Add to Home screen**.
* In iOS Safari: Tap **Share** -> **Add to Home Screen**.
