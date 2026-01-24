import requests

BASE = "http://127.0.0.1:8000"

def test_movie_topics_are_deduplicated():
    resp = requests.get(f"{BASE}/movie", params={"title": "Друзья"})
    assert resp.status_code == 200

    data = resp.json()
    topics = data.get("topics", [])
    assert topics, "topics empty"

    urls = [t["url"] for t in topics]
    assert len(urls) == len(set(urls)), "duplicate topic urls found"
