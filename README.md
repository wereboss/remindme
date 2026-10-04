# Notes & Reminders PWA (MVP 3)

A lightweight, responsive Progressive Web Application (PWA) for managing personal notes, tags, recurring reminders, and audio/web notifications, powered by Python (Flask) and SQLite. Designed with a thumb-friendly mobile-first user experience.

---

## Current Architecture & Baseline (MVP 3)

* **Server Binding:** Default host `0.0.0.0` and port `9031` (override via `PORT` environment variable).
* **Backend:** Python 3 + Flask application factory pattern (`app/`).
* **Database:** Embedded SQLite (`notes.sqlite`), with automatic schema migrations (`users`, `notes` with `tags`, `is_archived`, and `recurrence`).
* **Security & Multi-Tenancy:**
  * Open self-registration and credential-based login.
  * Passwords hashed via PBKDF2 (`werkzeug.security`).
  * Session-based authentication using HTTP-only cookies.
  * Strict per-user data isolation.
* **Notifications & Audio Alerts:**
  * Web Notifications API integration: native desktop and mobile push-style alerts when reminder deadlines arrive.
  * Web Audio API: Offline-capable synthetic two-tone harmonic chime (`587.33 Hz` -> `880 Hz`).
  * Alert deduplication via local session storage.
* **Recurring Reminders (In-Place Advancement):**
  * Configurable recurrence rules: `daily`, `weekly`, `monthly`.
  * Completing a recurring reminder automatically advances its deadline to the next interval and keeps it active.
  * Visual recurrence badge (`🔁 Daily`, `🔁 Weekly`, `🔁 Monthly`).
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
  * Service Worker (`/sw.js` cache `notes-pwa-v3`) precaching static UI assets for offline shell loading and fast app startup.
* **Cross-Platform Distribution:**
  * Standard Python Wheel (`.whl`) and Source distribution (`.tar.gz`).
  * Zero-config launchers for **Linux & macOS** (`launch.sh`) and **Windows** (`launch.bat`, `launch.ps1`).
  * Single command distribution packaging script (`scripts/package_dist.py`).

---

## Project Structure

```
├── app/
│   ├── __init__.py          # Flask app factory, blueprint registration & PWA routing
│   ├── __main__.py          # Console script & module entrypoint
│   ├── auth.py              # Authentication endpoints & login_required decorator
│   ├── db.py                # SQLite connection lifecycle & schema migrations
│   ├── notes.py             # Notes CRUD, search, tags, recurrence calculation & archival
│   ├── static/
│   │   ├── css/style.css    # Responsive styles, FAB styling, reminder badges & thumb targets
│   │   ├── icons/icon.svg   # Scalable PWA vector icon
│   │   ├── js/app.js        # Vanilla JS single-page app logic, Web Notifications & Web Audio
│   │   ├── manifest.json    # PWA Web App Manifest
│   │   └── sw.js            # Service Worker caching strategy (v3)
│   └── templates/
│       └── index.html       # HTML5 PWA shell with FAB, search bar, bell toggle & bottom sheets
├── scripts/
│   └── package_dist.py      # Cross-platform distribution packaging generator
├── tests/                   # Automated pytest suites
├── launch.sh                # Zero-config launcher for Linux & macOS
├── launch.bat               # Zero-config launcher for Windows Command Prompt
├── launch.ps1               # Zero-config launcher for Windows PowerShell
├── run.py                   # Server startup script (default: 0.0.0.0:9031)
├── setup.py                 # Setuptools build specification (wheel & sdist)
├── MANIFEST.in              # Package manifest for static & template bundling
├── requirements.txt         # Project dependencies (Flask, pytest)
├── spec.md                  # Current MVP specification
├── FAQ.md                   # Troubleshooting, test guide, and MVP 3 limitations
└── README.md                # Project documentation
```

---

## Quick Start (By Operating System)

### Linux & macOS
Simply execute the launcher script:
```bash
./launch.sh
```
The script automatically sets up a local `.venv`, installs dependencies, launches the server on `0.0.0.0:9031`, and opens your default browser.

### Windows
* **Command Prompt:** Double-click `launch.bat` or run:
  ```cmd
  launch.bat
  ```
* **PowerShell:**
  ```powershell
  .\launch.ps1
  ```

---

## Building Distribution Packages

To generate cross-platform distribution packages (Python Wheel, Source Tarball, and Portable ZIP):
```bash
python3 scripts/package_dist.py
```
Output packages in `dist/`:
1. `remindme_pwa-0.3.0-py3-none-any.whl`: Standard Python wheel installable via `pip install <wheel>` on any OS.
2. `remindme-pwa-0.3.0.tar.gz`: Source distribution.
3. `remindme-v0.3.0-portable.zip`: Complete zero-dependency zip containing launchers for Windows, macOS, and Linux.

---

## PWA Installation
* Open `http://localhost:9031` (or your machine's LAN IP address on port 9031) on your phone or desktop browser.
* **Android / Chrome:** Click the **Install** icon in the address bar or select **Add to Home screen**.
* **iOS / Safari:** Tap **Share** -> **Add to Home Screen**.
