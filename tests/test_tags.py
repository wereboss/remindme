from urllib.parse import quote

def test_create_and_filter_by_tags(auth_client):
    # Create notes with tags
    res1 = auth_client.post("/api/notes", json={
        "title": "Quarterly taxes",
        "tags": "finance, #urgent, work"
    })
    assert res1.status_code == 201
    note1 = res1.get_json()
    assert "finance" in note1["tags"]
    assert "urgent" in note1["tags"]
    assert "work" in note1["tags"]

    res2 = auth_client.post("/api/notes", json={
        "title": "Weekend hike",
        "tags": ["personal", "outdoors"]
    })
    assert res2.status_code == 201
    note2 = res2.get_json()
    assert "personal" in note2["tags"]
    assert "outdoors" in note2["tags"]

    # Filter by tag "finance"
    res_finance = auth_client.get("/api/notes?tag=finance")
    assert res_finance.status_code == 200
    finance_notes = res_finance.get_json()
    assert len(finance_notes) == 1
    assert finance_notes[0]["title"] == "Quarterly taxes"

    # Filter by tag with hash prefix (URL encoded %23urgent)
    res_urgent = auth_client.get(f"/api/notes?tag={quote('#urgent')}")
    assert res_urgent.status_code == 200
    urgent_notes = res_urgent.get_json()
    assert len(urgent_notes) == 1
    assert urgent_notes[0]["title"] == "Quarterly taxes"

    # Filter by query_string dict
    res_urgent_dict = auth_client.get("/api/notes", query_string={"tag": "#urgent"})
    assert res_urgent_dict.status_code == 200
    assert len(res_urgent_dict.get_json()) == 1

    # Filter by non-existent tag
    res_none = auth_client.get("/api/notes?tag=vacation")
    assert res_none.status_code == 200
    assert len(res_none.get_json()) == 0

def test_update_tags(auth_client):
    res = auth_client.post("/api/notes", json={"title": "Tag test", "tags": "initial"})
    note_id = res.get_json()["id"]

    # Update tags
    update_res = auth_client.put(f"/api/notes/{note_id}", json={
        "tags": "updated, refreshed"
    })
    assert update_res.status_code == 200
    updated_note = update_res.get_json()
    assert "updated" in updated_note["tags"]
    assert "refreshed" in updated_note["tags"]
    assert "initial" not in updated_note["tags"]
