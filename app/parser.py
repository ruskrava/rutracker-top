import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

PER_PAGE = 50
WORKERS = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_html(session: requests.Session, url: str) -> str:
    r = session.get(url, timeout=20)
    r.raise_for_status()
    return r.text

def parse_page(html: str) -> list[tuple[str, int]]:
    soup = BeautifulSoup(html, "lxml")
    rows = soup.select("tr.hl-tr")
    result = []

    for tr in rows:
        try:
            td = tr.find_all("td")
            title = (
                td[1]
                .select_one("a.torTopic")
                .get_text(strip=True)
                .split("/")[0]
            )
            stats = td[3].find_all("p")
            downloads = int(stats[1].get_text(strip=True).replace(",", ""))
            result.append((title, downloads))
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

def parse_forum(base_url: str) -> dict[str, int]:
    session = requests.Session()
    session.headers.update(HEADERS)

    total_pages = detect_total_pages(base_url)
    films: dict[str, int] = defaultdict(int)

    def worker(page: int):
        start = (page - 1) * PER_PAGE
        url = f"{base_url}&start={start}"
        html = get_html(session, url)
        return parse_page(html)

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(worker, p) for p in range(1, total_pages + 1)]
        for f in as_completed(futures):
            for title, downloads in f.result():
                films[title] += downloads

    return dict(films)
