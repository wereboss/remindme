# MVP 1 Specification: Core Notes & Visual Reminders PWA

## Current Baseline
* **Initial baseline (Greenfield project)**. No prior MVPs deployed.

---

## 1. Overview & Objectives
Build a lightweight, responsive Progressive Web Application (PWA) serving a notes and reminder service with a Python (Flask) backend and embedded SQLite database. Multi-user support is included with session-based authentication and strict per-user data isolation.

In MVP 1, reminders are modeled as notes with an optional deadline timestamp and are presented with visual indicators (Overdue, Due Today, Upcoming).

---

## 2. Technical Stack
* **Language & Runtime:** Python 3
* **Backend Framework:** Flask
* **Database:** SQLite (`sqlite3`) with schema migrations or initialization on startup
* **Security & Auth:** HTTP-only session cookies, password hashing via `werkzeug.security` (PBKDF2/scrypt)
* **Frontend:** Responsive vanilla HTML5, CSS3, and JavaScript (single-page interaction)
* **PWA Tier 1 Shell:** `manifest.json`, Service Worker (`sw.js`) caching static shell assets (HTML, CSS, JS, icons), enabling "Add to Home Screen" / installability
* **Testing:** `pytest` test suite covering models, authentication, security boundaries, and API endpoints

---

## 3. Data Models (`SQLite`)

### 3.1 `users` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique user identifier |
| `username` | TEXT | UNIQUE NOT NULL | Username for login (trimmed, min 3 chars) |
| `password_hash` | TEXT | NOT NULL | Securely hashed password |
| `created_at` | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

### 3.2 `notes` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique note identifier |
| `user_id` | INTEGER | NOT NULL, FOREIGN KEY(`users.id`) | Owner ID (strict isolation) |
| `title` | TEXT | NOT NULL | Note title (plain text) |
| `content` | TEXT | NOT NULL DEFAULT '' | Note body (plain text) |
| `deadline` | TEXT | NULL | Optional ISO-8601 string (e.g., `YYYY-MM-DDTHH:MM`) |
| `is_completed` | INTEGER | NOT NULL DEFAULT 0 | 0 = Active, 1 = Completed |
| `created_at` | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | Last modified timestamp |

---

## 4. API Endpoints

### 4.1 Authentication
* `POST /api/register`: Register new user (`username`, `password`). On success, set session cookie or return success.
* `POST /api/login`: Authenticate existing user (`username`, `password`). Sets secure HTTP-only session cookie.
* `POST /api/logout`: Clear session cookie.
* `GET /api/me`: Returns current authenticated user `{ id, username }` or 401 Unauthorized.

### 4.2 Notes & Reminders
All notes endpoints require an authenticated session. Queries must filter strictly by `user_id = session['user_id']`.
* `GET /api/notes`: Returns array of notes for the logged-in user.
  * Optional query params: `filter=all|reminders|completed`
  * Each note payload includes computed reminder status: `none`, `overdue`, `due_today`, or `upcoming`.
* `POST /api/notes`: Create note. Payload: `{ title, content, deadline (optional) }`.
* `GET /api/notes/<id>`: Retrieve specific note (404 if not found or belongs to another user).
* `PUT /api/notes/<id>`: Update note fields: `{ title, content, deadline, is_completed }`.
* `DELETE /api/notes/<id>`: Delete note (404 if not found or belongs to another user).

---

## 5. Visual Reminder Logic
For any note where `deadline` is present and `is_completed == 0`:
* **Overdue:** `deadline < current_time` (Red badge)
* **Due Today:** `deadline` falls within the current calendar day / within next 24 hours (Yellow/Orange badge)
* **Upcoming:** `deadline > today` (Blue/Neutral badge)
* If `is_completed == 1`: Marked as Completed (Green / strikethrough badge, regardless of deadline)

---

## 6. Frontend & PWA Specifications
* **Single Page Shell:**
  * Clean, responsive layout for mobile and desktop screens.
  * Auth view (Login / Register toggle) when unauthenticated.
  * Dashboard view when logged in with:
    * User header with username and Logout button.
    * Note creation form (title, content, optional datetime picker for deadline).
    * Filter tabs: "All Notes", "Reminders Only", "Completed".
    * Note cards displaying title, content, deadline, completion checkbox, edit/delete buttons, and color-coded status badges.
* **PWA Assets:**
  * `manifest.json`: Name, short name, start_url, display: standalone, theme_color, background_color, icons.
  * `sw.js`: Service worker to precache app shell (`/`, `/static/css/style.css`, `/static/js/app.js`, `/static/manifest.json`, icon assets).
  * Graceful handling when offline (shell loads with offline connectivity warning for server actions).

---

## 7. Testing Requirements (`pytest`)
* **Unit & Integration Tests in `tests/`:**
  1. `test_auth.py`: User registration, duplicate username handling, login success/failure, logout, and `/api/me`.
  2. `test_notes.py`: Create, read, update, delete notes; validation of title required.
  3. `test_isolation.py`: Strict isolation ensuring User A cannot read, update, or delete User B's notes.
  4. `test_reminders.py`: Verification of deadline status calculations (`overdue`, `due_today`, `upcoming`, and completed overrides).
* All tests must execute cleanly using `pytest tests/`.

---

## 8. Documentation Requirements
The Coder must create and maintain:
1. `README.md`:
   * Project description and architecture.
   * Prerequisites and installation instructions (`pip install -r requirements.txt`).
   * How to run the Flask application and how to access the PWA in a browser.
2. `FAQ.md`:
   * Troubleshooting common issues (e.g., database permissions, session cookies).
   * Testing procedures (how to run `pytest`).
   * Current MVP 1 limitations and what is deferred to MVP 2.

---

## 9. Future Iterations Backlog (Deferred to MVP 2+)
* Full-text search across titles and notes.
* Recurring / repeating reminder schedules.
* Categorization, tags, folders, or color tags.
* Archival / trash bin with recovery.
* Browser Web Notifications API & sound chimes.
