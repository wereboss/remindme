def test_search_title_and_content(auth_client):
    # Setup notes
    auth_client.post("/api/notes", json={
        "title": "Groceries list",
        "content": "Buy organic avocados and sourdough bread"
    })
    auth_client.post("/api/notes", json={
        "title": "Meeting notes",
        "content": "Discuss sprint planning and roadmap"
    })
    auth_client.post("/api/notes", json={
        "title": "Avocado recipes",
        "content": "Guacamole and toast"
    })

    # Search title match
    res_title = auth_client.get("/api/notes?q=meeting")
    assert res_title.status_code == 200
    notes = res_title.get_json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Meeting notes"

    # Search content match
    res_content = auth_client.get("/api/notes?q=sourdough")
    assert res_content.status_code == 200
    notes = res_content.get_json()
    assert len(notes) == 1
    assert notes[0]["title"] == "Groceries list"

    # Search multiple matches (case-insensitive)
    res_multi = auth_client.get("/api/notes?q=AVOCADO")
    assert res_multi.status_code == 200
    notes = res_multi.get_json()
    assert len(notes) == 2
    titles = [n["title"] for n in notes]
    assert "Groceries list" in titles
    assert "Avocado recipes" in titles

    # Search non-matching
    res_empty = auth_client.get("/api/notes?q=nonexistentkeyword123")
    assert res_empty.status_code == 200
    assert len(res_empty.get_json()) == 0

def test_search_user_isolation(client):
    # User 1 creates confidential note
    client.post("/api/register", json={"username": "user1", "password": "pass12345"})
    client.post("/api/notes", json={"title": "SuperSecretTitle", "content": "ClassifiedContent"})
    client.post("/api/logout")

    # User 2 registers and searches
    client.post("/api/register", json={"username": "user2", "password": "pass12345"})
    res = client.get("/api/notes?q=SuperSecretTitle")
    assert res.status_code == 200
    assert len(res.get_json()) == 0

    res_content = client.get("/api/notes?q=ClassifiedContent")
    assert res_content.status_code == 200
    assert len(res_content.get_json()) == 0
