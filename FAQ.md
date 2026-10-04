# Frequently Asked Questions & Troubleshooting (FAQ)

## 1. Testing Procedures

### How do I run the automated tests?
Run `pytest` with the `--tb=short` flag from the project root:
```bash
pytest --tb=short
```
Or run verbose tests:
```bash
pytest -v
```

### What does the test suite cover in MVP 2?
The test suite validates:
* **Authentication**: Registration, password hashing, session login, logout, and `/api/me`.
* **Multi-User Data Isolation**: Verification that User A cannot read, update, search, or delete notes created by User B.
* **Notes CRUD**: Creating, reading, editing, and deleting notes with validation of required fields.
* **Reminder Logic**: Accurate categorization of reminder states (`overdue`, `due_today`, `upcoming`, and `completed`).
* **Search**: Real-time keyword matching across `title` and `content` without cross-user leakage.
* **Tags & Categorization**: Adding tags, updating tags, and filtering active notes by tag.
* **Archival (Soft-Delete)**: Archiving notes, filtering by `filter=archived`, unarchiving/restoring, and ensuring archived notes are excluded from standard views.

---

## 2. Cross-Platform Launchers & Distribution

### Q: How do I run on Windows without installing manual tools?
**A**: Ensure Python 3.10+ is installed from python.org with the "Add Python to PATH" option checked. Then simply double-click `launch.bat`. It will create an isolated virtual environment (`.venv`), install dependencies, launch the server on port 9031, and open your browser automatically.

### Q: On macOS/Linux, `launch.sh` reports "permission denied"?
**A**: Ensure the executable bit is set on the script:
```bash
chmod +x launch.sh
./launch.sh
```

### Q: How can I distribute RemindMe to end users?
**A**: Run `python3 scripts/package_dist.py`. It builds:
* A standalone zero-config ZIP archive (`remindme-v0.2.0-portable.zip`) ready to unzip and run on any desktop OS.
* A standard Python wheel (`.whl`) installable via `pip install <wheel>` exposing the `remindme` console command.

---

## 3. Operations & Troubleshooting

### Q: Why is the server listening on port 9031?
**A**: In MVP 2, the default port was updated from 5000 to 9031, binding to `0.0.0.0` so it can be accessed over local area networks or reverse proxies. To change the port, set the `PORT` environment variable before running:
```bash
PORT=8080 python3 run.py
```

### Q: How does the Floating Action Button (FAB) work on mobile?
**A**: The FAB is positioned in the lower-right thumb zone with a touch target exceeding 56px. Tapping it opens a thumb-accessible bottom sheet on mobile screens, making single-handed note and reminder creation fluid without scrolling.

### Q: What happened to existing databases from MVP 1?
**A**: The application includes automatic non-destructive column migrations in `app/db.py`. When launched against an existing `notes.sqlite` file, it checks for `tags` and `is_archived` columns and applies `ALTER TABLE` statements automatically without data loss.

---

## 4. Known Limitations in MVP 2 & Backlog for MVP 3

While MVP 2 brings search, categorization, archival, and mobile thumb ergonomics, the following features remain scoped for **MVP 3**:
* **Push / Audio Notifications**: Reminders currently rely on visual status badges. Client-side Web Notification API alerts and sound chimes will be introduced in MVP 3.
* **Recurring Reminders**: Setting repeat rules (e.g., daily, weekly, monthly) that spawn the next reminder upon completion.
* **Markdown Rendering**: Note bodies remain plain text for lightweight performance; rich formatting/markdown will be added in a future iteration.
