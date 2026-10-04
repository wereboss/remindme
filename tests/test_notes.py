def test_create_and_get_note(auth_client):
    # Create note
    res = auth_client.post("/api/notes", json={
        "title": "Buy groceries",
        "content": "Apples, milk, bread"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["title"] == "Buy groceries"
    assert data["content"] == "Apples, milk, bread"
    assert data["is_completed"] is False
    assert data["status"] == "none"
    note_id = data["id"]

    # Get single note
    get_res = auth_client.get(f"/api/notes/{note_id}")
    assert get_res.status_code == 200
    assert get_res.get_json()["title"] == "Buy groceries"

    # List notes
    list_res = auth_client.get("/api/notes")
    assert list_res.status_code == 200
    notes = list_res.get_json()
    assert len(notes) == 1
    assert notes[0]["id"] == note_id

def test_create_note_validation(auth_client):
    # Missing title
    res = auth_client.post("/api/notes", json={"title": "   ", "content": "No title here"})
    assert res.status_code == 400
    assert "error" in res.get_json()

    # Invalid deadline format
    res_bad_date = auth_client.post("/api/notes", json={
        "title": "Invalid date note",
        "deadline": "not-a-date"
    })
    assert res_bad_date.status_code == 400

def test_update_note(auth_client):
    res = auth_client.post("/api/notes", json={"title": "Draft blog", "content": "Initial ideas"})
    note_id = res.get_json()["id"]

    # Update title and mark as completed
    update_res = auth_client.put(f"/api/notes/{note_id}", json={
        "title": "Published blog",
        "is_completed": True
    })
    assert update_res.status_code == 200
    data = update_res.get_json()
    assert data["title"] == "Published blog"
    assert data["is_completed"] is True
    assert data["status"] == "completed"

def test_delete_note(auth_client):
    res = auth_client.post("/api/notes", json={"title": "Temporary note"})
    note_id = res.get_json()["id"]

    # Delete
    del_res = auth_client.delete(f"/api/notes/{note_id}")
    assert del_res.status_code == 200

    # Verify 404
    get_res = auth_client.get(f"/api/notes/{note_id}")
    assert get_res.status_code == 404

def test_unauthenticated_access_blocked(client):
    # Unauthenticated requests to /api/notes must return 401
    assert client.get("/api/notes").status_code == 401
    assert client.post("/api/notes", json={"title": "Test"}).status_code == 401
    assert client.get("/api/notes/1").status_code == 401
    assert client.put("/api/notes/1", json={"title": "Test"}).status_code == 401
    assert client.delete("/api/notes/1").status_code == 401
