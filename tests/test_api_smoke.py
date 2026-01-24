import requests

BASE = "http://127.0.0.1:8000"

def test_status():
    r = requests.get(f"{BASE}/status")
    assert r.status_code == 200

def test_top():
    r = requests.get(f"{BASE}/top?n=3")
    assert r.status_code == 200

def test_movie():
    r = requests.get(f"{BASE}/movie", params={"title": "Дюна"})
    assert r.status_code == 200
