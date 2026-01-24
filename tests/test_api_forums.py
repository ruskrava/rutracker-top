from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_forums_list_and_reset():
    r = client.get("/forums")
    assert r.status_code == 200
    assert "forums" in r.json()

    r = client.post("/reset")
    assert r.status_code == 200
    data = r.json()
    assert data["forums"] == 0
    assert data["items"] == 0

def test_delete_nonexistent_forum():
    r = client.delete("/forum", params={"url": "https://example.com"})
    assert r.status_code == 200
    assert r.json()["status"] == "not_found"
