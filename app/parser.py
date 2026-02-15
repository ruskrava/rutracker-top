import requests
import time
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

PER_PAGE = 50
WORKERS = 10
RETRIES = 3
RETRY_DELAY = 2

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def normalize_title(raw: str) -> str:
    raw = raw.strip()

    match = re.search(r"\[(\d{4}),", raw)
    year = match.group(1) if match else None

    title_ru = raw.split("/")[0].strip()

    if year:
        return f"[{year}] {title_ru}"

    return title_ru


def get_html(session: requests.Session, url: str) -> str:
    last_exc = None
    for attempt in range(RETRIES):
        try:
            r = session.get(url, timeout=20)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last_exc = e
            if attempt < RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise last_exc


def parse_page_with_link(html: str) -> list[tuple[str, int, str]]:
    soup = BeautifulSoup(html, "lxml")
    rows = soup.select("tr.hl-tr")
    result = []

    for tr in rows:
        try:
            td = tr.find_all("td")
            a = td[1].select_one("a.torTopic")

            raw_title = a.get_text(" ", strip=True)
            title = normalize_title(raw_title)

            link = "https://rutracker.org/forum/" + a.get("href")
            stats = td[3].find_all("p")
            downloads = int(stats[1].get_text(strip=True).replace(",", ""))

            result.append((title, downloads, link))
        except Exception:
            continue

    return result


def detect_total_pages(base_url: str) -> int:
    session = requests.Session()
    session.headers.update(HEADERS)

    low, high = 0, 200
    last_good = 0

    while low <= high:
        mid = (low + high) // 2
        url = f"{base_url}&start={mid * PER_PAGE}"
        html = get_html(session, url)

        if "hl-tr" in html:
            last_good = mid
            low = mid + 1
        else:
            high = mid - 1

    return last_good + 1


def parse_forum_aggregated(base_url: str) -> dict[str, dict]:
    session = requests.Session()
    session.headers.update(HEADERS)

    total_pages = detect_total_pages(base_url)
    films: dict[str, dict] = {}

    def worker(page: int):
        start = (page - 1) * PER_PAGE
        url = f"{base_url}&start={start}"
        html = get_html(session, url)
        return parse_page_with_link(html)

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(worker, p) for p in range(1, total_pages + 1)]
        for f in as_completed(futures):
            for title, downloads, link in f.result():
                if title not in films:
                    films[title] = {"downloads": 0, "topics": []}
                films[title]["downloads"] += downloads
                films[title]["topics"].append({
                    "url": link,
                    "downloads": downloads
                })

    return films
