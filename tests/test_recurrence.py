from datetime import datetime, timedelta
from app.notes import calculate_next_deadline

def test_calculate_next_deadline_helper():
    base_str = "2026-10-04T10:00:00"

    # Daily: +1 day
    daily_res = calculate_next_deadline(base_str, "daily")
    assert daily_res == "2026-10-05T10:00:00"

    # Weekly: +7 days
    weekly_res = calculate_next_deadline(base_str, "weekly")
    assert weekly_res == "2026-10-11T10:00:00"

    # Monthly: +1 month
    monthly_res = calculate_next_deadline(base_str, "monthly")
    assert monthly_res == "2026-11-04T10:00:00"

    # None: unchanged
    none_res = calculate_next_deadline(base_str, "none")
    assert none_res == base_str

def test_create_recurring_note(auth_client):
    deadline = "2026-10-15T09:00"

    # Valid daily
    res = auth_client.post("/api/notes", json={
        "title": "Daily Standup",
        "deadline": deadline,
        "recurrence": "daily"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["recurrence"] == "daily"
    assert data["deadline"] == deadline

    # Invalid recurrence
    res_bad = auth_client.post("/api/notes", json={
        "title": "Bad recurrence",
        "deadline": deadline,
        "recurrence": "yearly"
    })
    assert res_bad.status_code == 400
    assert "error" in res_bad.get_json()

def test_recurring_note_advance_on_completion(auth_client):
    initial_deadline = "2026-10-20T14:00:00"

    # Create weekly note
    res = auth_client.post("/api/notes", json={
        "title": "Weekly Status Report",
        "deadline": initial_deadline,
        "recurrence": "weekly"
    })
    note_id = res.get_json()["id"]

    # Mark as completed
    update_res = auth_client.put(f"/api/notes/{note_id}", json={
        "is_completed": True
    })
    assert update_res.status_code == 200
    updated_data = update_res.get_json()

    # Under Option A: In-place advancement
    assert updated_data["was_recurring_advanced"] is True
    assert updated_data["is_completed"] is False
    assert updated_data["deadline"] == "2026-10-27T14:00:00"

def test_non_recurring_note_normal_completion(auth_client):
    # Create non-recurring note
    res = auth_client.post("/api/notes", json={
        "title": "One-off Task",
        "deadline": "2026-10-20T14:00:00",
        "recurrence": "none"
    })
    note_id = res.get_json()["id"]

    # Mark as completed
    update_res = auth_client.put(f"/api/notes/{note_id}", json={
        "is_completed": True
    })
    assert update_res.status_code == 200
    updated_data = update_res.get_json()

    assert updated_data["was_recurring_advanced"] is False
    assert updated_data["is_completed"] is True
    assert updated_data["status"] == "completed"

def test_recurring_note_isolation(client):
    # User 1 creates daily note
    client.post("/api/register", json={"username": "rec_user1", "password": "password123"})
    res1 = client.post("/api/notes", json={
        "title": "User 1 Daily Habit",
        "deadline": "2026-10-10T08:00:00",
        "recurrence": "daily"
    })
    note1_id = res1.get_json()["id"]
    client.post("/api/logout")

    # User 2 logs in and cannot advance User 1's note
    client.post("/api/register", json={"username": "rec_user2", "password": "password123"})
    put_res = client.put(f"/api/notes/{note1_id}", json={"is_completed": True})
    assert put_res.status_code == 404
