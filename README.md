# Rutracker Top

Rutracker Top is a FastAPI-based service for parsing RuTracker forums and building
aggregated TOP movie lists based on download statistics.

The project focuses on:
- background forum parsing
- fast access to aggregated data
- persistence across restarts
- simple and controllable architecture without a database

---

## What is this

The service parses selected RuTracker forum sections, aggregates statistics for
the same movies across multiple topics and forums, and exposes an HTTP API for
retrieving TOP lists and detailed movie information.

The project was originally designed as a **local self-hosted service**.
The HTTP API acts as an internal layer used by the web interface.

---

## Current features (implemented)

- Multi-forum parsing
- Global aggregation across all forums
- Topic deduplication by URL
- Background parsing using worker threads
- Thread-safe data access (`threading.RLock`)
- Persistent on-disk cache (`pickle`)
- Atomic cache saving
- Fast startup with cache restore
- Built-in scheduler
- Runtime scheduler control via API
- Forum management via API
- Health-check endpoint
- Deterministic API and parser tests

---

## API

### POST /parse?url=...
Starts background parsing for a forum URL.

- Only one parsing task can run at a time
- Concurrent requests are ignored
- The forum URL is validated before execution

Response example:
{ "status": "started" }

---

### GET /status
Returns current service status.

Fields:
- status — parsing state (idle, running, done, error)
- forums — number of tracked forums
- items — number of aggregated movies
- last_url — last parsed forum URL

---

### GET /top?n=10
Returns TOP-N movies by total download count aggregated across all forums.

Query parameters:
- n — number of items to return (1–500)

---

### GET /movie?title=...
Returns aggregated data for a single movie:
- total download count
- list of topics with URLs and download statistics

---

### GET /forums
Returns the list of currently tracked forums.

---

### DELETE /forum?url=...
Removes a forum from the dataset and rebuilds global aggregation.

---

### POST /reset
Resets all data and clears the persistent cache.

---

### Scheduler control

- GET /schedule/status
- POST /schedule/enable?interval=...
- POST /schedule/disable

The scheduler:
- runs in a background thread
- uses a shared interval for all forums
- skips execution if the service is busy

---

### GET /health
Health-check endpoint for monitoring and container orchestration.

---

## Architecture

- FastAPI application
- Single-process design
- Background parsing using threads
- In-memory shared data structures:
  - DATA["forums"]
  - DATA["global"]
- Thread-safe access using RLock
- Persistent cache stored on disk using pickle
- No database

---

## Service vision

Rutracker Top is evolving into a local self-hosted service with a web interface.

The intended usage scenario:
- open a local service page in the browser
- configure a list of RuTracker forums to track
- enable automatic background updates
- browse TOP movies and detailed movie statistics

The HTTP API remains a stable internal contract used by the service UI.

---

## Web UI (planned)

The planned web interface is a simple static page served by the same FastAPI
application.

Planned UI functionality:
- forum list management (add / remove)
- scheduler configuration (enable / interval)
- TOP-N movies table
- movie detail view with aggregated statistics and links

The UI explicitly does not include:
- authentication
- user accounts
- a database
- public SaaS access

The project remains a single-user local service.

---

## Deployment model

The project targets Docker-based deployment.

Planned deployment setup:
- FastAPI service container (API + UI)
- persistent volume for data/cache.pkl
- configuration via environment variables
- access through a reverse proxy (e.g. Nginx)

Local execution without Docker remains supported.

---

## Limitations

- Single-process service
- Only one active parsing task at a time
- Parser is tightly coupled to RuTracker HTML structure
- No authentication or access control
- Not intended for public or high-load production usage

---

## Roadmap

### Phase 1 — Core (completed)
- FastAPI-based API
- Forum parser
- Global aggregation
- Topic deduplication
- Persistent cache
- Scheduler
- Thread safety
- Deterministic tests
- Documentation

### Phase 2 — Service mode
- Static web UI
- UI built on top of existing API
- Forum management via browser
- Scheduler control via UI
- Parsing progress visibility

### Phase 3 — Docker-first
- Dockerfile
- docker-compose setup
- Persistent volume for cache
- Example Nginx reverse-proxy configuration

### Phase 4 — UX and robustness
- Improved error handling
- Retry / backoff logic in parser
- Manual refresh actions
- UI auto-refresh and status updates

---

## Notes

This project does not store or redistribute any content.
It only processes publicly available statistics and links.
