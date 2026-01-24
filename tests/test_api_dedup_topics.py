from fastapi.testclient import TestClient
from app.api import app, DATA, rebuild_global

client = TestClient(app)

def test_movie_topics_are_deduplicated():
    DATA["forums"] = {
        "test_forum": {
            "Друзья": {
                "downloads": 10,
                "topics": [
                    {"url": "u1", "downloads": 5},
                    {"url": "u1", "downloads": 5},
                ],
            }
        }
    }
    rebuild_global()

    resp = client.get("/movie", params={"title": "Друзья"})
    assert resp.status_code == 200

    topics = resp.json().get("topics", [])
    assert topics
    urls = [t["url"] for t in topics]
    assert len(urls) == len(set(urls))
