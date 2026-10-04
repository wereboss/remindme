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

### What does the test suite cover in MVP 3?
The test suite validates:
* **Authentication**: Registration, password hashing, session login, logout, and `/api/me`.
* **Multi-User Data Isolation**: Verification that User A cannot read, update, search, or delete notes created by User B.
* **Notes CRUD**: Creating, reading, editing, and deleting notes with validation of required fields.
* **Reminder Logic**: Accurate categorization of reminder states (`overdue`, `due_today`, `upcoming`, and `completed`).
* **Search**: Real-time keyword matching across `title` and `content` without cross-user leakage.
* **Tags & Categorization**: Adding tags, updating tags, and filtering active notes by tag.
* **Archival (Soft-Delete)**: Archiving notes, filtering by `filter=archived`, unarchiving/restoring, and ensuring archived notes are excluded from standard views.
* **Recurring Reminders**: Calculation of next deadlines for daily, weekly, and monthly recurrence; in-place deadline advancement when checking off recurring tasks; normal completion for non-recurring tasks.

---

## 2. Notifications & Audio Troubleshooting

### Q: Why aren't browser notifications appearing?
**A**: Ensure you have granted notification permissions:
1. Click the "🔔 Alerts" button in the app header and choose "Allow" when prompted by your browser.
2. In browser settings (Chrome: `chrome://settings/content/notifications`), verify that `http://localhost:9031` (or your host domain) is not listed under "Not allowed to send notifications".
3. Note that some operating systems (macOS Focus / Windows Focus Assist) may suppress notification popups if "Do Not Disturb" is active.

### Q: Does the audio chime require downloading audio files?
**A**: No. The chime is synthesized dynamically at runtime using the browser's built-in Web Audio API oscillator. It produces zero network traffic and functions 100% offline.

---

## 3. Recurring Reminders

### Q: What happens when I check off a recurring reminder?
**A**: Under our In-Place Advancement model (Option A), completing a recurring reminder immediately calculates the next deadline date (e.g., +1 day for daily, +7 days for weekly, +1 calendar month for monthly) and leaves the task active in your reminders list. A brief toast notification confirms the advancement.

---

## 4. Cross-Platform Launchers & Distribution

### Q: How do I run on Windows without installing manual tools?
**A**: Ensure Python 3.10+ is installed from python.org with the "Add Python to PATH" option checked. Then simply double-click `launch.bat`. It will create an isolated virtual environment (`.venv`), install dependencies, launch the server on port 9031, and open your browser automatically.

### Q: On macOS/Linux, `launch.sh` reports "permission denied"?
**A**: Ensure the executable bit is set on the script:
```bash
chmod +x launch.sh
./launch.sh
```

### Q: How can I build release distribution packages?
**A**: Run `python3 scripts/package_dist.py`. It builds:
* A standalone zero-config ZIP archive (`remindme-v0.3.0-portable.zip`) ready to unzip and run on any desktop OS.
* A standard Python wheel (`remindme_pwa-0.3.0-py3-none-any.whl`) installable via `pip install <wheel>`.
* A source distribution (`remindme-pwa-0.3.0.tar.gz`).
