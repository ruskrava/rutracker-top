from fastapi import FastAPI, Query
from typing import Dict
from app.parser import parse_forum_aggregated
import threading
import pickle, os

app = FastAPI(title="Rutracker Top API")

DATA: Dict[str, int] = {}
STATUS = "idle"
LAST_URL = None

DATA_PATH = "data/cache.pkl"


def load_cache():
    global DATA
    if not os.path.exists(DATA_PATH):
        return
    try:
        with open(DATA_PATH, "rb") as f:
            obj = pickle.load(f)
            DATA = obj.get("data", {})
    except Exception:
        pass
        pass




def background_parse(url: str):
    global DATA, STATUS, LAST_URL
    STATUS = "running"
    LAST_URL = url
    try:
        DATA = parse_forum_aggregated(url)
        # removed v2
        save_cache()
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
    top = sorted(DATA.items(), key=lambda x: x[1]["downloads"], reverse=True)[:n]
    return [
        {"rank": i + 1, "title": title, "downloads": cnt["downloads"]}
        for i, (title, cnt) in enumerate(top)
    ]




load_cache()

def save_cache():
    tmp = DATA_PATH + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump({"data": DATA}, f)
    os.replace(tmp, DATA_PATH)

@app.get("/movie")
def get_movie(title: str):
    return DATA.get(title, {})
