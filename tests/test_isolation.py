def test_user_data_isolation(client):
    # User A registers and creates a secret note
    client.post("/api/register", json={"username": "userA", "password": "passwordA123"})
    res_a = client.post("/api/notes", json={
        "title": "User A Private Note",
        "content": "Secret information"
    })
    assert res_a.status_code == 201
    note_a_id = res_a.get_json()["id"]

    # User A logs out
    client.post("/api/logout")

    # User B registers
    client.post("/api/register", json={"username": "userB", "password": "passwordB123"})
    
    # User B lists notes - should NOT see User A's note
    res_b_list = client.get("/api/notes")
    assert res_b_list.status_code == 200
    assert len(res_b_list.get_json()) == 0

    # User B attempts to access User A's note by ID - should return 404
    assert client.get(f"/api/notes/{note_a_id}").status_code == 404

    # User B attempts to update User A's note - should return 404
    assert client.put(f"/api/notes/{note_a_id}", json={"title": "Hacked"}).status_code == 404

    # User B attempts to delete User A's note - should return 404
    assert client.delete(f"/api/notes/{note_a_id}").status_code == 404

    # User B logs out, User A logs back in
    client.post("/api/logout")
    client.post("/api/login", json={"username": "userA", "password": "passwordA123"})

    # Note A is still intact for User A
    res_verify = client.get(f"/api/notes/{note_a_id}")
    assert res_verify.status_code == 200
    assert res_verify.get_json()["title"] == "User A Private Note"
