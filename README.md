# Rutracker Top

Version: 1.1.0

Rutracker Top is a self-hosted FastAPI service that parses selected RuTracker forum sections and builds aggregated TOP movie lists based on download statistics.

The service is designed for local or LAN deployment.

---

## Features

- Multi-forum parsing
- Global aggregation across all added forums
- Topic deduplication by URL
- Background parsing (threaded)
- Thread-safe in-memory storage (RLock)
- Persistent cache (pickle, atomic save)
- Fast startup with cache restore
- Built-in scheduler (runtime configurable)
- REST API (v1 frozen contract)
- Mobile-first web UI with infinite scroll
- Docker-ready deployment
- Health endpoint for monitoring

---

## Quick Start (Docker)

Create a data directory:

~~bash
mkdir data
~~

Run the container:

~~bash
docker run -d \
  -p 8000:8000 \
  -v "$(pwd)/data:/app/data" \
  --name rutracker-top \
  ghcr.io/ruskrava/rutracker-top:1.1.0
~~

Open in browser:

http://<SERVER_IP>:8000/static/index.html

---

## Docker Compose

Example docker-compose.yml:

~~yaml
services:
  rutracker-top:
    image: ghcr.io/ruskrava/rutracker-top:1.1.0
    container_name: rutracker-top
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      SCHEDULER_ENABLED: "false"
      SCHEDULER_INTERVAL: "3600"
    restart: unless-stopped
~~

Run:

~~bash
docker compose up -d
~~

---

## API (v1 — Frozen Contract)

### POST /parse?url=...

Response:

~~json
{ "status": "started" }
~~

### GET /status

~~json
{
  "status": "idle | running | done | error",
  "forums": 2,
  "items": 500,
  "last_url": "https://..."
}
~~

### GET /top?offset=0&limit=50

~~json
{
  "items": [
    {
      "rank": 1,
      "title": "[2026] Movie Title",
      "downloads": 12345
    }
  ],
  "offset": 0,
  "limit": 50,
  "total": 1000,
  "has_more": true
}
~~

### GET /movie?title=...

~~json
{
  "downloads": 12345,
  "topics": [
    {
      "url": "...",
      "downloads": 5000
    }
  ]
}
~~

### GET /forums

### DELETE /forum?url=...

### POST /reset

### Scheduler

- GET /schedule/status
- POST /schedule/enable?interval=...
- POST /schedule/disable

Minimum interval: 60 seconds.

### GET /health

---

## Architecture

- FastAPI
- Single-process service
- ThreadPoolExecutor for parsing
- In-memory DATA structure
- Persistent cache in data/cache.pkl
- No database

---

## Limitations

- Single process
- One active parsing task at a time
- No authentication
- Not intended for public high-load usage
- Depends on RuTracker HTML structure

---

## Legal Notice

This project does not host or distribute copyrighted content.
It only processes publicly available metadata and statistics.
