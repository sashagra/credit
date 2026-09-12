import os
import tempfile
import pytest
from main import app, get_db, init_db

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config["DATABASE"] = db_path
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    os.close(db_fd)
    os.unlink(db_path)

def test_home_page(client):
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"Hello" in rv.data or "кредит" in rv.data.decode("utf-8").lower()

def test_apply_page_get(client):
    rv = client.get("/apply")
    assert rv.status_code == 200

def test_apply_post(client):
    rv = client.post("/apply", json={
        "name": "Иван",
        "amount": 100000,
        "term": 12,
    })
    assert rv.status_code == 200 or rv.status_code == 201
    data = rv.get_json()
    assert data["status"] == "в ожидании"

def test_applications_page(client):
    rv = client.get("/applications")
    assert rv.status_code == 200

def test_applications_api(client):
    rv = client.get("/api/applications")
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, list)

def test_update_status(client):
    # create application
    client.post("/apply", json={
        "name": "Петр",
        "amount": 50000,
        "term": 6,
    })
    rv = client.patch("/api/applications/1/status", json={"status": "одобрено"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["status"] == "одобрено"

def test_applications_api_returns_pending(client):
    client.post("/apply", json={"name": "Алиса", "amount": 30000, "term": 24})
    rv = client.get("/api/applications")
    data = rv.get_json()
    assert any(a["status"] == "в ожидании" for a in data)
