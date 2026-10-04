from datetime import datetime, timedelta

def test_reminder_status_calculation(auth_client):
    now = datetime.now()

    # 1. Past deadline (Overdue)
    past_deadline = (now - timedelta(days=2)).isoformat()
    res_past = auth_client.post("/api/notes", json={
        "title": "Overdue Task",
        "deadline": past_deadline
    })
    assert res_past.status_code == 201
    assert res_past.get_json()["status"] == "overdue"

    # 2. Today's deadline (Due Today)
    # Set to today at 23:59:59 to guarantee same calendar date in the future today
    today_deadline = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()
    res_today = auth_client.post("/api/notes", json={
        "title": "Due Today Task",
        "deadline": today_deadline
    })
    assert res_today.status_code == 201
    assert res_today.get_json()["status"] == "due_today"

    # 3. Future deadline (Upcoming)
    future_deadline = (now + timedelta(days=5)).isoformat()
    res_future = auth_client.post("/api/notes", json={
        "title": "Upcoming Task",
        "deadline": future_deadline
    })
    assert res_future.status_code == 201
    assert res_future.get_json()["status"] == "upcoming"

    # 4. Note without deadline
    res_none = auth_client.post("/api/notes", json={"title": "General Note"})
    assert res_none.status_code == 201
    assert res_none.get_json()["status"] == "none"

    # 5. Overdue note marked completed
    overdue_id = res_past.get_json()["id"]
    res_completed = auth_client.put(f"/api/notes/{overdue_id}", json={"is_completed": True})
    assert res_completed.status_code == 200
    assert res_completed.get_json()["status"] == "completed"

def test_filter_reminders_and_completed(auth_client):
    now = datetime.now()
    future = (now + timedelta(days=1)).isoformat()

    # Create plain note
    auth_client.post("/api/notes", json={"title": "Plain Note"})

    # Create active reminder
    res_rem = auth_client.post("/api/notes", json={
        "title": "Active Reminder",
        "deadline": future
    })
    rem_id = res_rem.get_json()["id"]

    # Create completed reminder
    res_done = auth_client.post("/api/notes", json={
        "title": "Finished Reminder",
        "deadline": future
    })
    done_id = res_done.get_json()["id"]
    auth_client.put(f"/api/notes/{done_id}", json={"is_completed": True})

    # Test filter=reminders (should only return active reminders)
    res_reminders = auth_client.get("/api/notes?filter=reminders")
    assert res_reminders.status_code == 200
    reminders = res_reminders.get_json()
    assert len(reminders) == 1
    assert reminders[0]["id"] == rem_id

    # Test filter=completed (should only return completed notes)
    res_comp = auth_client.get("/api/notes?filter=completed")
    assert res_comp.status_code == 200
    completed = res_comp.get_json()
    assert len(completed) == 1
    assert completed[0]["id"] == done_id

    # Test filter=all
    res_all = auth_client.get("/api/notes?filter=all")
    assert res_all.status_code == 200
    assert len(res_all.get_json()) == 3
