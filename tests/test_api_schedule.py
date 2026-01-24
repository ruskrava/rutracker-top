from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_schedule_status():
    r = client.get("/schedule/status")
    assert r.status_code == 200
    data = r.json()
    assert "enabled" in data
    assert "interval" in data

def test_schedule_enable_with_interval():
    r = client.post("/schedule/enable", params={"interval": 120})
    assert r.status_code == 200
    data = r.json()
    assert data["enabled"] is True
    assert data["interval"] == 120

    r = client.get("/schedule/status")
    data = r.json()
    assert data["enabled"] is True
    assert data["interval"] == 120

def test_schedule_disable():
    r = client.post("/schedule/disable")
    assert r.status_code == 200
    assert r.json()["enabled"] is False

    r = client.get("/schedule/status")
    assert r.json()["enabled"] is False

def test_schedule_enable_invalid_interval():
    r = client.post("/schedule/enable", params={"interval": 10})
    assert r.status_code == 422
