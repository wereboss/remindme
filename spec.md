# MVP 3 Specification: Notifications & Recurring Reminders

## Current Baseline (MVP 2)
* Python Flask backend on `0.0.0.0:9031` with SQLite database.
* Multi-user session authentication with strict tenant isolation.
* Note and reminder CRUD with visual status indicators (`overdue`, `due_today`, `upcoming`, `completed`).
* Live full-text search across titles and contents.
* Tags categorization with chip filtering.
* Archival / soft-delete system.
* Mobile thumb-friendly UX with Floating Action Button (FAB) and bottom-sheet modal.
* Cross-platform distribution packaging (`setup.py`, `launch.sh`, `launch.bat`, `launch.ps1`, `scripts/package_dist.py`).
* 18 automated tests passing in `tests/`.
* Published to remote GitHub repository.

---

## 1. Overview & Objectives for MVP 3
1. **Browser Web Notifications & Audio Chime:**
   * Prompt user for Web Notification permission via an in-app toggle.
   * Background monitoring timer alerting the user when an active reminder's deadline is reached.
   * Play an offline-capable synthetic audio chime via the browser's Web Audio API.
   * Deduplicate alerts to avoid repeated nagging.
2. **Recurring Reminders (In-Place Advancement - Option A):**
   * Support recurrence schedules: `none`, `daily`, `weekly`, `monthly`.
   * When a recurring reminder is marked completed, automatically advance its deadline to the next recurrence interval and reset `is_completed = 0` (active).
   * Visual recurrence badges on note cards.
3. **Automated Testing & Packaging:**
   * Pytest coverage for recurrence deadline calculations and completion behavior.
   * Version bump to `0.3.0` and cross-platform release package generation.

---

## 2. Database Schema Updates (`SQLite`)
* Add `recurrence TEXT NOT NULL DEFAULT 'none'` to `notes` table (allowed: `'none'`, `'daily'`, `'weekly'`, `'monthly'`).
* Automatic column migration in `init_db()` for backward compatibility.

---

## 3. Recurrence Logic & API Specifications

### 3.1 Deadline Advancement Rule
When a note with an active `deadline` and `recurrence in ('daily', 'weekly', 'monthly')` is marked completed via `PUT /api/notes/<id>`:
* **Daily:** Advance deadline by `+1 day` (preserving time of day).
* **Weekly:** Advance deadline by `+7 days`.
* **Monthly:** Advance deadline by `+1 calendar month` (or approx. 30 days if month end overflow).
* **Completion Status:** The note remains active (`is_completed = 0`) with the new `deadline`.
* Notes with `recurrence == 'none'` behave as normal (`is_completed = 1`).

### 3.2 Endpoints (`POST /api/notes`, `PUT /api/notes/<id>`)
* Accept `recurrence` in JSON payload.
* Validate that `recurrence` is one of `['none', 'daily', 'weekly', 'monthly']`.
* Return computed recurrence in note payload.

---

## 4. Frontend & Notification Specifications

### 4.1 Notifications & Audio Chime
* **Permission Toggle:** An accessible bell button in the header. Shows status (`disabled`, `enabled`, or `unsupported`).
* **Reminder Monitor:** Periodic timer in `app.js` (every 30 seconds) checking active notes with deadlines against client system time.
* **Alert Trigger:**
  * When `deadline <= now` and status is overdue/due_today and note has not yet been notified in the current session:
    * Displays browser Notification: `Reminder: [Title]` with content snippet and app icon.
    * Sounds a gentle two-tone chime via Web Audio API (`587.33 Hz` -> `880 Hz`).
    * Records alerted note ID in `sessionStorage`/`localStorage` to prevent duplicate alerts.

### 4.2 UI Enhancements
* **Recurrence Selector:** Dropdown in Create/Edit modal with options:
  * "Does not repeat" (`none`)
  * "Every Day" (`daily`)
  * "Every Week" (`weekly`)
  * "Every Month" (`monthly`)
* **Badges:** Note cards display recurrence badge (e.g. `🔁 Daily`, `🔁 Weekly`, `🔁 Monthly`).
* **Toast Notification:** Feedback message when completing a recurring reminder (e.g. "Recurring reminder advanced to [Next Date]").

---

## 5. Testing Requirements (`pytest`)
* New test file `tests/test_recurrence.py`:
  1. Test recurrence calculation functions for daily, weekly, and monthly intervals.
  2. Test `POST /api/notes` with recurrence saves and returns recurrence value.
  3. Test completing a recurring note advances the deadline and keeps `is_completed=0`.
  4. Test completing a non-recurring note sets `is_completed=1`.
  5. Test user isolation remains strict with recurring notes.
* All tests must execute cleanly with `pytest --tb=short`.

---

## 6. Post-MVP Standard Packaging Directives
* Bump project version to `0.3.0` in `setup.py` and `scripts/package_dist.py`.
* Execute `python3 scripts/package_dist.py` to regenerate wheel, source tarball, and portable zip bundle.
* Update `README.md` and `FAQ.md` reflecting the new baseline.
* Commit code and release packages to Git and tag `v0.3.0`.
