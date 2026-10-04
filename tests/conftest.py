import os
import tempfile
import pytest
from app import create_app
from app.db import init_db

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    test_config = {
        "TESTING": True,
        "DATABASE": db_path,
        "SECRET_KEY": "test-key-notes-pwa",
    }
    app = create_app(test_config)

    with app.app_context():
        init_db()

    yield app

    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Client with an already registered and logged-in default user."""
    client.post("/api/register", json={"username": "alice", "password": "password123"})
    return client

class AuthActions:
    def __init__(self, client):
        self._client = client

    def register(self, username="testuser", password="password123"):
        return self._client.post(
            "/api/register",
            json={"username": username, "password": password}
        )

    def login(self, username="testuser", password="password123"):
        return self._client.post(
            "/api/login",
            json={"username": username, "password": password}
        )

    def logout(self):
        return self._client.post("/api/logout")

@pytest.fixture
def auth(client):
    return AuthActions(client)
