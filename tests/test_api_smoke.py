from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)


def test_status():
    r = client.get("/status")
    assert r.status_code == 200


def test_top_available():
    r = client.get("/top")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert "has_more" in data


def test_movie_available():
    r = client.get("/movie", params={"title": "Дюна"})
    assert r.status_code == 200
