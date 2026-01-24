from fastapi import FastAPI, Query
from typing import Dict
from app.parser import parse_forum, parse_forum_with_topics
import threading

app = FastAPI(title="Rutracker Top API")

DATA: Dict[str, int] = {}
DATA_V2 = {}
STATUS = "idle"
LAST_URL = None


def background_parse(url: str):
    global DATA, DATA_V2, STATUS, LAST_URL
    STATUS = "running"
    LAST_URL = url
    try:
        DATA = parse_forum(url)
        DATA_V2 = parse_forum_with_topics(url)
        STATUS = "done"
    except Exception as e:
        STATUS = f"error: {e}"


@app.post("/parse")
def start_parse(url: str = Query(..., description="Forum URL")):
    if STATUS == "running":
        return {"status": STATUS, "message": "Already running"}
    thread = threading.Thread(target=background_parse, args=(url,), daemon=True)
    thread.start()
    return {"status": "started"}


@app.get("/status")
def get_status():
    return {"status": STATUS, "items": len(DATA)}


@app.get("/top")
def get_top(n: int = Query(10, ge=1, le=500)):
    top = sorted(DATA.items(), key=lambda x: x[1], reverse=True)[:n]
    return [
        {
            "rank": i + 1,
            "title": title,
            "downloads": cnt,
        }
        for i, (title, cnt) in enumerate(top)
    ]


@app.get("/top_v2")
def get_top_v2(n: int = Query(10, ge=1, le=500)):
    if not DATA_V2:
        return []

    data = DATA_V2

    top = sorted(
        data.items(),
        key=lambda x: x[1]["downloads"],
        reverse=True
    )[:n]

    result = []
    for i, (title, info) in enumerate(top):
        best = max(info["topics"], key=lambda t: t["downloads"])
        result.append({
            "rank": i + 1,
            "title": title,
            "downloads": info["downloads"],
            "best_topic_url": best["url"],
        })

    return result
