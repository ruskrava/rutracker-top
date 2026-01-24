from fastapi import FastAPI, Query
from app.parser import parse_forum_aggregated
import threading
import pickle
import os
import time

app = FastAPI(title="Rutracker Top API")

DATA = {"forums": {}, "global": {}}
STATUS = "idle"
LAST_URL = None

DATA_PATH = "data/cache.pkl"

os.makedirs("data", exist_ok=True)

# Scheduler config (ENV-based, docker-friendly)
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "false").lower() == "true"
SCHEDULER_INTERVAL = int(os.getenv("SCHEDULER_INTERVAL", "3600"))


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


def load_cache():
    global DATA
    if not os.path.exists(DATA_PATH):
        return
    try:
        with open(DATA_PATH, "rb") as f:
            raw = pickle.load(f)

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


def scheduler_loop():
    while True:
        time.sleep(SCHEDULER_INTERVAL)
        if not SCHEDULER_ENABLED:
            continue
        if STATUS != "idle":
            continue
        urls = list(DATA["forums"].keys())
        for url in urls:
            if STATUS != "idle":
                break
            try:
                background_parse(url)
            except Exception:
                pass


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
    movie = DATA["global"].get(title, {})
    if movie and "topics" in movie:
        movie["topics"] = sorted(
            movie["topics"],
            key=lambda t: t["downloads"],
            reverse=True
        )
    return movie


@app.get("/forums")
def list_forums():
    return {
        "count": len(DATA["forums"]),
        "forums": list(DATA["forums"].keys())
    }


@app.delete("/forum")
def delete_forum(url: str):
    if url not in DATA["forums"]:
        return {"status": "not_found", "url": url}
    del DATA["forums"][url]
    rebuild_global()
    save_cache()
    return {
        "status": "deleted",
        "url": url,
        "forums": len(DATA["forums"]),
        "items": len(DATA["global"])
    }


@app.post("/reset")
def reset_all():
    global DATA, STATUS, LAST_URL
    DATA = {"forums": {}, "global": {}}
    STATUS = "idle"
    LAST_URL = None
    save_cache()
    return {"status": "reset", "forums": 0, "items": 0}


# Scheduler control (runtime)
@app.get("/schedule/status")
def schedule_status():
    return {
        "enabled": SCHEDULER_ENABLED,
        "interval": SCHEDULER_INTERVAL,
    }


@app.post("/schedule/enable")
def schedule_enable(interval: int = Query(..., ge=60)):
    global SCHEDULER_ENABLED, SCHEDULER_INTERVAL
    SCHEDULER_INTERVAL = interval
    SCHEDULER_ENABLED = True
    return {"enabled": True, "interval": SCHEDULER_INTERVAL}


@app.post("/schedule/disable")
def schedule_disable():
    global SCHEDULER_ENABLED
    SCHEDULER_ENABLED = False
    return {"enabled": False}


load_cache()

# start scheduler thread (always running, behavior controlled via flags)
threading.Thread(target=scheduler_loop, daemon=True).start()
