import logging

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s [%(levelname)s] %(message)s"

)

logger = logging.getLogger(__name__)

from fastapi import FastAPI, Query
from app.parser import parse_forum_aggregated
import threading
import pickle
import os
import time
import re

app = FastAPI(title="Rutracker Top API")

DATA = {"forums": {}, "global": {}}
STATUS = "idle"
LAST_URL = None

DATA_PATH = "data/cache.pkl"

os.makedirs("data", exist_ok=True)

# Thread safety
data_lock = threading.RLock()

# Scheduler config (ENV-based)
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "false").lower() == "true"
SCHEDULER_INTERVAL = int(os.getenv("SCHEDULER_INTERVAL", "3600"))


def validate_forum_url(url: str) -> bool:
    if not isinstance(url, str) or not url:
        return False
    if not (url.startswith("http://") or url.startswith("https://")):
        return False
    if "rutracker.org/forum/" not in url:
        return False
    if re.search(r"[?&]f=\d+", url):
        return True
    return False


def rebuild_global():
    with data_lock:
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
                "topics": [
                    {"url": u, "downloads": d}
                    for u, d in data["topics"].items()
                ],
            }
            for title, data in merged.items()
        }


def load_cache():
    logger.info("Loading cache from disk")
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
    logger.info("Saving cache to disk")
    with data_lock:
        tmp = DATA_PATH + ".tmp"
        with open(tmp, "wb") as f:
            pickle.dump(DATA, f)
        os.replace(tmp, DATA_PATH)
        logger.info("Cache saved successfully")


def background_parse(url: str):
    logger.info("Parsing started: %s", url)
    global STATUS, LAST_URL

    with data_lock:
        STATUS = "running"
        LAST_URL = url

    try:
        result = parse_forum_aggregated(url)

        with data_lock:
            DATA["forums"][url] = result
            rebuild_global()
            save_cache()
            STATUS = "done"
            logger.info("Parsing done: %s", url)
    except Exception as e:
        logger.error("Parsing failed: %s", url, exc_info=True)
        with data_lock:
            STATUS = f"error: {e}"


def scheduler_loop():
    logger.info("Scheduler loop started")
    while True:
        time.sleep(SCHEDULER_INTERVAL)
        logger.info("Scheduler tick")
        if not SCHEDULER_ENABLED:
            logger.info("Scheduler skipped (disabled)")
            continue
        if STATUS != "idle":
            logger.info("Scheduler skipped (busy)")
            continue

        urls = list(DATA["forums"].keys())
        for url in urls:
            if STATUS != "idle":
                logger.info("Scheduler skipped (busy)")
                break
            try:
                background_parse(url)
            except Exception:
                logger.error("Scheduler error", exc_info=True)
                pass


@app.post("/parse")
def start_parse(url: str = Query(..., description="Forum URL")):
    if not validate_forum_url(url):
        return {"status": "error", "message": "invalid forum url"}
    if STATUS == "running":
        return {"status": STATUS, "message": "Already running"}
    threading.Thread(
        target=background_parse, args=(url,), daemon=True
    ).start()
    return {"status": "started"}


@app.get("/status")
def get_status():
    with data_lock:
        return {
            "status": STATUS,
            "forums": len(DATA["forums"]),
            "items": len(DATA["global"]),
            "last_url": LAST_URL,
        }


@app.get("/top")
def get_top(n: int = Query(10, ge=1, le=500)):
    with data_lock:
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
    with data_lock:
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
    with data_lock:
        return {
            "count": len(DATA["forums"]),
            "forums": list(DATA["forums"].keys())
        }


@app.delete("/forum")
def delete_forum(url: str):
    if not validate_forum_url(url):
        return {"status": "error", "message": "invalid forum url"}
    with data_lock:
        if url not in DATA["forums"]:
            return {"status": "not_found", "url": url}
        del DATA["forums"][url]

    rebuild_global()
    save_cache()

    with data_lock:
        return {
            "status": "deleted",
            "url": url,
            "forums": len(DATA["forums"]),
            "items": len(DATA["global"])
        }


@app.post("/reset")
def reset_all():
    global DATA, STATUS, LAST_URL
    with data_lock:
        DATA = {"forums": {}, "global": {}}
        STATUS = "idle"
        LAST_URL = None

    save_cache()
    return {"status": "reset", "forums": 0, "items": 0}


# Scheduler control
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
threading.Thread(target=scheduler_loop, daemon=True).start()


@app.get("/health")
def health():
    return {"status": "ok", "service": "rutracker-top"}
