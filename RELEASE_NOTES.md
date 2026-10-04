# Release v0.3.0 — Notes & Reminders PWA

A lightweight, multi-user Progressive Web Application (PWA) for managing personal notes, tags, recurring reminders, and audio/web notifications, powered by Python (Flask) and SQLite.

---

## What's New in v0.3.0

### 🔔 Web Notifications & Offline Audio Chimes
* **Browser Push-Style Alerts:** Native desktop and mobile notifications triggered automatically when reminder deadlines arrive.
* **Web Audio API Chime:** Built-in two-tone synthetic chime (`587.33 Hz` -> `880 Hz`) synthesized dynamically at runtime — 100% offline, zero audio files required.
* **Notification Toggle:** Thumb-accessible bell toggle in the header navigation with session alert deduplication.

### 🔁 Recurring Reminders (In-Place Advancement)
* **Recurrence Schedules:** Set reminders to repeat **Daily**, **Weekly**, or **Monthly**.
* **In-Place Advancement:** When checked off, recurring tasks immediately calculate and schedule their next deadline timestamp while remaining active.
* **Visual Recurrence Badges:** Clear indicator badges (`🔁 Daily`, `🔁 Weekly`, `🔁 Monthly`) on note cards.

### 📱 Mobile Thumb-Friendly Ergonomics
* **Floating Action Button (FAB):** 58px FAB (`+`) fixed in the bottom-right corner for single-handed thumb creation.
* **Bottom-Sheet Modal:** Smooth slide-up bottom sheet on mobile screens for effortless note creation and editing.
* **Optimized Touch Targets:** All interactive controls (buttons, chips, checkboxes) meet or exceed the 44px touch target standard.

### 🔍 Discovery & Organization
* **Full-Text Search:** Instant debounced search bar filtering across note titles and contents.
* **Tags System:** Add normalized tags (e.g. `#work`, `#personal`, `#urgent`) with clickable chip filters.
* **Archival System (Soft-Delete):** Archive inactive notes to keep the active dashboard clean, with dedicated **Archive** tab and one-click restore.

### 🔒 Multi-Tenant Security & Runtime
* **Multi-User Isolation:** Open registration and session-based login with strict tenant boundaries (`user_id`).
* **Server Binding:** Default host `0.0.0.0` and port `9031` (configurable via `PORT` environment variable).

---

## Direct Deployment & Download Packages

| Asset | Platform / Environment | Description |
| :--- | :--- | :--- |
| **`remindme-v0.3.0-portable.zip`** | **Linux, macOS & Windows** | Zero-configuration portable bundle with native launcher scripts. |
| **`remindme_pwa-0.3.0-py3-none-any.whl`** | **Python (Any OS)** | Standard Python wheel installable via `pip`. Exposes `remindme` CLI. |
| **`remindme-pwa-0.3.0.tar.gz`** | **Source Archive** | Full source package. |

---

## Quick Deployment Instructions

### 1. Linux & macOS (Zero-Config)
1. Download and extract `remindme-v0.3.0-portable.zip`.
2. In terminal, run:
   ```bash
   chmod +x launch.sh
   ./launch.sh
   ```
3. Opens browser automatically at `http://localhost:9031`.

### 2. Windows (Zero-Config)
1. Download and extract `remindme-v0.3.0-portable.zip`.
2. Double-click `launch.bat` (or in PowerShell run `.\launch.ps1`).
3. Opens browser automatically at `http://localhost:9031`.

### 3. Python Wheel (`pip`)
```bash
pip install remindme_pwa-0.3.0-py3-none-any.whl
remindme
```

---

## Package Integrity (SHA-256 Checksums)

```
f99104a6360b797d5947bb51e769ad7c6cb94ff721513e37bba505f35247bab8  remindme-pwa-0.3.0.tar.gz
a1655fb5c83404aa799d6aae24f6a1f8ac0e61018b1c27998f17179485d16e18  remindme-v0.3.0-portable.zip
21cf2ce48d7ee1163b2b80703fbd8bbd3e708cfdd1adaddefd2fdf5fcff08d99  remindme_pwa-0.3.0-py3-none-any.whl
```
