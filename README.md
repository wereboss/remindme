# Notes & Reminders PWA (MVP 2)

A lightweight, responsive Progressive Web Application (PWA) for managing personal notes, tags, and visual reminders, powered by Python (Flask) and SQLite. Designed with a thumb-friendly mobile-first user experience.

---

## Current Architecture & Baseline (MVP 2)

* **Server Binding:** Default host `0.0.0.0` and port `9031` (override via `PORT` environment variable).
* **Backend:** Python 3 + Flask application factory pattern (`app/`)
* **Database:** Embedded SQLite (`notes.sqlite`), with automatic schema creation and migrations (`users`, `notes` with `tags` and `is_archived`).
* **Security & Multi-Tenancy:**
  * Open self-registration and credential-based login.
  * Passwords hashed via PBKDF2 (`werkzeug.security`).
  * Session-based authentication using HTTP-only cookies.
  * Strict per-user data isolation.
* **Thumb-Friendly Mobile UX & FAB:**
  * Floating Action Button (FAB: `+`) fixed in the bottom-right corner for effortless thumb-reach on mobile devices.
  * Bottom-sheet modal animation for creating and editing notes.
  * Touch targets formatted to minimum 44px for thumb tap ergonomics.
* **Search & Categorization:**
  * Live search bar filtering titles and plaintext content simultaneously.
  * Tags system: Add tags (e.g. `work`, `urgent`) to notes, display tag chips, and filter notes with interactive tag clicks.
* **Archival (Soft-Delete):**
  * Archive completed or inactive notes to keep the active dashboard clean.
  * Dedicated **Archive** filter tab with one-click **Restore** or permanent deletion.
* **Visual Reminders:**
  * ⚠️ **Overdue** (Red badge): deadline has passed.
  * 🔔 **Due Today** (Orange badge): deadline is due today / within 24 hours.
  * 📅 **Upcoming** (Blue badge): future deadline.
  * ✓ **Completed** (Green badge / strikethrough): toggled complete.
* **PWA Tier 1 Shell:**
  * Web App Manifest (`/static/manifest.json`) with standalone display mode.
  * Service Worker (`/sw.js`) precaching static UI assets for offline shell loading and fast app startup.

---

## Project Structure

```
├── app/
│   ├── __init__.py          # Flask app factory, blueprint registration & PWA routing
│   ├── auth.py              # Authentication endpoints & login_required decorator
│   ├── db.py                # SQLite connection lifecycle & schema migration (tags, is_archived)
│   ├── notes.py             # Notes CRUD, search, tag filters, archival & status calculation
│   ├── static/
│   │   ├── css/style.css    # Responsive styles, FAB styling, reminder badges & thumb targets
│   │   ├── icons/icon.svg   # Scalable PWA vector icon
│   │   ├── js/app.js        # Vanilla JS single-page app logic, FAB modals & Service Worker
│   │   ├── manifest.json    # PWA Web App Manifest
│   │   └── sw.js            # Service Worker caching strategy
│   └── templates/
│       └── index.html       # HTML5 PWA shell with FAB, search bar & bottom sheets
├── tests/                   # Automated pytest suites
├── run.py                   # Server startup script (default: 0.0.0.0:9031)
├── requirements.txt         # Project dependencies (Flask, pytest)
├── spec.md                  # Current MVP specification
├── FAQ.md                   # Troubleshooting, test guide, and MVP 2 limitations
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
By default, the server binds to `0.0.0.0:9031`. Open `http://localhost:9031` in your browser.

### 4. PWA Installation
* Open `http://localhost:9031` in Chrome, Chromium, or Safari (iOS).
* In Chrome / Android: Click the **Install** icon in the address bar or select **Add to Home screen**.
* In iOS Safari: Tap **Share** -> **Add to Home Screen**.
