# MVP 2 Specification: Organization, Thumb-Friendly Mobile UX & Server Configuration

## Current Baseline (MVP 1)
* Flask application factory pattern with SQLite database (`users`, `notes`).
* Session-based authentication with strict multi-user tenant isolation.
* Note and reminder unified model with visual status indicators (`overdue`, `due_today`, `upcoming`, `completed`).
* Tier 1 PWA installable shell (`manifest.json`, `sw.js`).
* Comprehensive test suite in `tests/` with 11 passing tests.
* Committed and synchronized with GitHub remote `main`.

---

## 1. Overview & Objectives for MVP 2
Expand the application to improve mobile usability and organization:
1. **Server Configuration:** Default binding to `0.0.0.0` and port `9031`.
2. **Thumb-Friendly Mobile UX:** Implement a Floating Action Button (FAB) for note creation, mobile bottom reachability, and touch-target optimization (minimum 44px touch targets).
3. **Search:** Real-time keyword search across note titles and content.
4. **Tags & Categorization:** Add custom tags to notes with interactive chip filters.
5. **Archival System:** Soft-delete/archival mechanism to declutter the dashboard, with a dedicated Archive view and unarchive/restore support.

---

## 2. Server & Port Configuration
* `run.py` must default to host `0.0.0.0` and port `9031` (configurable via `PORT` environment variable).
* Update [README.md](file:///workspace/README.md) and [FAQ.md](file:///workspace/FAQ.md) instructions to reference port `9031`.

---

## 3. Database Schema Updates (`SQLite`)
Ensure backward compatibility with automatic schema migration during `init_db()`:
* **`notes` Table Alterations:**
  * Add `tags TEXT NOT NULL DEFAULT ''` (comma-separated list of clean, lowercased tags, e.g. `work,personal`).
  * Add `is_archived INTEGER NOT NULL DEFAULT 0` (0 = active, 1 = archived).

---

## 4. API Endpoints & Query Enhancements

### 4.1 Notes Listing & Search (`GET /api/notes`)
* Query Parameters:
  * `filter`: `all` (default active notes), `reminders` (active reminders), `completed` (active completed notes), `archived` (archived notes).
  * `q`: Optional search keyword. Performs case-insensitive matching across `title` and `content`.
  * `tag`: Optional tag filter. Returns notes that include the specified tag.
* Rules:
  * Standard views (`all`, `reminders`, `completed`) MUST exclude notes where `is_archived == 1`.
  * The `archived` view MUST return only notes where `is_archived == 1`.

### 4.2 Note Creation & Updating (`POST /api/notes`, `PUT /api/notes/<id>`)
* Accept `tags` in payload (string or array of strings, stored as normalized comma-separated string).
* Accept `is_archived` boolean flag in `PUT /api/notes/<id>` to allow archiving / restoring notes.

---

## 5. Frontend & Thumb-Friendly Mobile UX
* **Floating Action Button (FAB):**
  * Position a circular, thumb-reachable FAB (`+`) fixed in the bottom-right corner of the mobile viewport.
  * Tapping the FAB opens an accessible modal / slide-up sheet to create a new note or reminder.
* **Thumb Ergonomics:**
  * Touch targets (buttons, filter chips, checkboxes, inputs) sized to at least 44px height/width.
  * Easy-to-reach filter bar and search input.
* **Search & Tag UI:**
  * Clean search bar at the top of the dashboard with instant search-as-you-type (or debounced).
  * Tag chips on note cards (e.g., `#work`, `#personal`).
  * Clickable tag chips to filter notes by that tag.
* **Archival Actions:**
  * Note cards include an "Archive" action (or "Restore" if viewed in the Archive tab).

---

## 6. Testing Requirements (`pytest`)
* Create/update automated tests in `tests/`:
  1. `test_search.py`: Verify searching by title and content returns expected matches; verify cross-user isolation during search.
  2. `test_tags.py`: Verify adding tags, updating tags, and filtering by tag.
  3. `test_archive.py`: Verify archiving a note removes it from active views; verify `filter=archived` lists archived notes; verify restoring unarchives a note.
* All tests must execute cleanly with `pytest --tb=short`.

---

## 7. Documentation Directives
* Update [README.md](file:///workspace/README.md) with port `9031`, FAB usage, and new search/tag/archive features.
* Update [FAQ.md](file:///workspace/FAQ.md) with updated test instructions and remaining MVP 3 backlog items (Push/Audio notifications, Recurring reminders).
