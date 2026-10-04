def test_archive_and_unarchive(auth_client):
    # Create note
    res = auth_client.post("/api/notes", json={
        "title": "Old Task",
        "content": "Completed long ago"
    })
    note_id = res.get_json()["id"]

    # Archive via endpoint
    arch_res = auth_client.post(f"/api/notes/{note_id}/archive")
    assert arch_res.status_code == 200
    assert arch_res.get_json()["is_archived"] is True

    # Note must NOT appear in default active list
    list_active = auth_client.get("/api/notes")
    assert list_active.status_code == 200
    active_ids = [n["id"] for n in list_active.get_json()]
    assert note_id not in active_ids

    # Note must appear in archive view
    list_archived = auth_client.get("/api/notes?filter=archived")
    assert list_archived.status_code == 200
    archived_ids = [n["id"] for n in list_archived.get_json()]
    assert note_id in archived_ids

    # Unarchive note
    unarch_res = auth_client.post(f"/api/notes/{note_id}/unarchive")
    assert unarch_res.status_code == 200
    assert unarch_res.get_json()["is_archived"] is False

    # Note reappears in active list
    list_reappeared = auth_client.get("/api/notes")
    assert list_reappeared.status_code == 200
    reappeared_ids = [n["id"] for n in list_reappeared.get_json()]
    assert note_id in reappeared_ids

def test_archive_via_put(auth_client):
    res = auth_client.post("/api/notes", json={"title": "Put Archive Test"})
    note_id = res.get_json()["id"]

    # Update is_archived = True via PUT
    put_res = auth_client.put(f"/api/notes/{note_id}", json={"is_archived": True})
    assert put_res.status_code == 200
    assert put_res.get_json()["is_archived"] is True

    # Verify excluded from active list
    active_list = auth_client.get("/api/notes")
    assert note_id not in [n["id"] for n in active_list.get_json()]

def test_archive_isolation(client):
    # User 1 creates note
    client.post("/api/register", json={"username": "archuser1", "password": "password123"})
    res1 = client.post("/api/notes", json={"title": "User 1 Note"})
    note_id = res1.get_json()["id"]
    client.post("/api/logout")

    # User 2 tries to archive User 1's note
    client.post("/api/register", json={"username": "archuser2", "password": "password123"})
    assert client.post(f"/api/notes/{note_id}/archive").status_code == 404
    assert client.post(f"/api/notes/{note_id}/unarchive").status_code == 404
