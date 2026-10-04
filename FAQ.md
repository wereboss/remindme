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

### What does the test suite cover?
The test suite validates:
* **Authentication**: Registration, password hashing, session login, logout, and `/api/me`.
* **Multi-User Data Isolation**: Verification that User A cannot read, update, or delete notes created by User B.
* **Notes CRUD**: Creating, reading, editing, and deleting notes with validation of required fields.
* **Reminder Logic**: Accurate categorization of reminder states (`overdue`, `due_today`, `upcoming`, and `completed`).

---

## 2. Troubleshooting & Operations

### Q: Why does the app say "Session expired" or "Unauthorized"?
**A**: Ensure cookies are enabled in your browser. The application uses secure HTTP-only cookies (`Lax` SameSite policy) to manage user sessions across requests. If running behind a reverse proxy in production, ensure `X-Forwarded-Proto` and `SESSION_COOKIE_SECURE` are configured appropriately.

### Q: Where is the SQLite database file stored?
**A**: By default, SQLite stores data in the Flask instance folder: `instance/notes.sqlite`. If you need to reset the local database, you can safely remove the `instance/notes.sqlite` file; the schema will automatically regenerate on the next server startup.

### Q: Why isn't the Service Worker updating after editing static files?
**A**: Service workers cache static assets aggressively. To force an update:
1. Increment `CACHE_NAME` in `app/static/sw.js`.
2. In Chrome DevTools, navigate to **Application -> Service Workers** and click **Unregister** or check **Update on reload**.

---

## 3. Known Limitations in MVP 1

As scoped in `spec.md`, MVP 1 focuses strictly on core note-taking, multi-user isolation, and visual deadline tracking. The following features are explicitly deferred to **MVP 2+**:
* **Push / Audio Notifications**: Reminders in MVP 1 are visual indicators only; browser push notifications and audio alerts will arrive in MVP 2.
* **Full-Text Search**: Notes cannot be searched by keyword yet; filtering is currently limited to "All", "Reminders", and "Completed".
* **Recurrence**: Reminders are one-off deadlines without recurrence rules (e.g. daily/weekly).
* **Tags & Categories**: Notes do not yet support color tags or folder organization.
* **Archival**: Deleting a note is permanent; soft-delete/archival will be added in MVP 2.
