def test_register_success(client):
    res = client.post("/api/register", json={"username": "bob", "password": "securepass12"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["user"]["username"] == "bob"
    assert "id" in data["user"]

    # Verify session is active after registration
    me_res = client.get("/api/me")
    assert me_res.status_code == 200
    assert me_res.get_json()["username"] == "bob"

def test_register_validation(client):
    # Username too short
    res = client.post("/api/register", json={"username": "ab", "password": "securepass12"})
    assert res.status_code == 400
    assert "error" in res.get_json()

    # Password too short
    res = client.post("/api/register", json={"username": "validname", "password": "12"})
    assert res.status_code == 400

    # Duplicate username
    client.post("/api/register", json={"username": "uniqueuser", "password": "password123"})
    dup_res = client.post("/api/register", json={"username": "uniqueuser", "password": "password456"})
    assert dup_res.status_code == 409

def test_login_and_logout(client):
    client.post("/api/register", json={"username": "charlie", "password": "mypassword"})
    client.post("/api/logout")

    # Access /api/me when logged out
    res = client.get("/api/me")
    assert res.status_code == 401

    # Bad login
    bad_login = client.post("/api/login", json={"username": "charlie", "password": "wrongpassword"})
    assert bad_login.status_code == 401

    # Good login
    good_login = client.post("/api/login", json={"username": "charlie", "password": "mypassword"})
    assert good_login.status_code == 200
    assert good_login.get_json()["user"]["username"] == "charlie"

    # Verify session
    me_res = client.get("/api/me")
    assert me_res.status_code == 200
    assert me_res.get_json()["username"] == "charlie"

    # Logout
    logout_res = client.post("/api/logout")
    assert logout_res.status_code == 200

    # Verify session cleared
    me_res2 = client.get("/api/me")
    assert me_res2.status_code == 401
