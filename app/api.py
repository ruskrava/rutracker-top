from fastapi import FastAPI, Query
from app.parser import parse_forum_aggregated
import threading
import pickle, os

app = FastAPI(title="Rutracker Top API")

DATA = {"forums": {}, "global": {}}
STATUS = "idle"
LAST_URL = None

DATA_PATH = "data/cache.pkl"




def load_cache():
    global DATA
    if not os.path.exists(DATA_PATH):
        return
    try:
        with open(DATA_PATH, "rb") as f:
            raw = pickle.load(f)

        # old single-forum format
        if "forums" not in raw:
            DATA = {"forums": {"legacy": raw}, "global": {}}
            rebuild_global()
        else:
            DATA = raw
    except Exception:
        DATA = {"forums": {}, "global": {}}


def save_cache():
    tmp = DATA_PATH + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(DATA, f)
    os.replace(tmp, DATA_PATH)


def background_parse(url: str):
    global STATUS, LAST_URL
    STATUS = "running"
    LAST_URL = url
    try:
        DATA["forums"][url] = parse_forum_aggregated(url)
        rebuild_global()
        save_cache()
        STATUS = "done"
    except Exception as e:
        STATUS = f"error: {e}"


@app.post("/parse")
def start_parse(url: str = Query(..., description="Forum URL")):
    if STATUS == "running":
        return {"status": STATUS, "message": "Already running"}
    threading.Thread(target=background_parse, args=(url,), daemon=True).start()
    return {"status": "started"}


@app.get("/status")
def get_status():
    return {
        "status": STATUS,
        "forums": len(DATA["forums"]),
        "items": len(DATA["global"]),
        "last_url": LAST_URL,
    }


@app.get("/top")
def get_top(n: int = Query(10, ge=1, le=500)):
    top = sorted(
        DATA["global"].items(),
        key=lambda x: x[1]["downloads"],
        reverse=True
    )[:n]
    return [
        {"rank": i + 1, "title": title, "downloads": info["downloads"]}
        for i, (title, info) in enumerate(top)
    ]


@app.get("/movie")
def get_movie(title: str):
    return DATA["global"].get(title, {})


load_cache()
def rebuild_global():
    merged = {}
    for forum_data in DATA["forums"].values():
        for title, info in forum_data.items():
            m = merged.setdefault(title, {"downloads": 0, "topics": {}})
            m["downloads"] += info["downloads"]
            for t in info["topics"]:
                m["topics"][t["url"]] = t["downloads"]

    DATA["global"] = {
        title: {
            "downloads": data["downloads"],
            "topics": [{"url": u, "downloads": d} for u, d in data["topics"].items()],
        }
        for title, data in merged.items()
    }
