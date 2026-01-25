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

The project was originally designed as a local self-hosted service.
The HTTP API acts as an internal layer used by the web interface.

---

## Current features (implemented)

- Multi-forum parsing
- Global aggregation across all forums
- Topic deduplication by URL
- Background parsing using worker threads
- Thread-safe data access (threading.RLock)
- Persistent on-disk cache (pickle)
- Atomic cache saving
- Fast startup with cache restore
- Built-in scheduler
- Runtime scheduler control via API
- Forum management via API
- Health-check endpoint

---

## Quick start (Docker — recommended)

The service is distributed as a ready-to-run Docker image via
GitHub Container Registry.

Requirements:
- Docker

Run the service with a single command:

docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --name rutracker-top \
  ghcr.io/ruskrava/rutracker-top:latest

After startup:

Web UI:
http://localhost:8000/static/index.html

API:
http://localhost:8000

All data is stored in ./data/cache.pkl and persists across container restarts.

---

## API

POST /parse?url=...
Starts background parsing for a forum URL.

Rules:
- Only one parsing task can run at a time
- Concurrent requests are ignored
- The forum URL is validated before execution

Response example:
{ "status": "started" }

---

GET /status
Returns current service status.

Fields:
- status — parsing state (idle, running, done, error)
- forums — number of tracked forums
- items — number of aggregated movies
- last_url — last parsed forum URL

---

GET /top?n=10
Returns TOP-N movies by total download count aggregated across all forums.

Query parameters:
- n — number of items to return (1–500)

---

GET /movie?title=...
Returns aggregated data for a single movie:
- total download count
- list of topics with URLs and download statistics

---

GET /forums
Returns the list of currently tracked forums.

---

DELETE /forum?url=...
Removes a forum from the dataset and rebuilds global aggregation.

---

POST /reset
Resets all data and clears the persistent cache.

---

GET /health
Health-check endpoint for monitoring and container orchestration.

---

## Scheduler control

GET /schedule/status  
POST /schedule/enable?interval=...  
POST /schedule/disable  

The scheduler:
- runs in a background thread
- uses a shared interval for all forums
- does not start immediately
- first execution happens after the interval delay
- skips execution if the service is busy

Minimum allowed interval: 60 seconds.

Scheduler activity is visible only in application logs.


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

The HTTP API is considered an internal contract.
API v1 is frozen and should not be changed without explicit agreement.


---

## Deployment model

The project targets Docker-based deployment.

Recommended setup:
- single service container
- persistent volume for data/cache.pkl
- configuration via environment variables
- access via local network or reverse proxy

The Docker image is published via GitHub Container Registry.

Local execution without Docker remains supported for development purposes.

---

## Limitations

- Single-process service
- Only one active parsing task at a time
- Parser is tightly coupled to RuTracker HTML structure
- No authentication or access control
- Not intended for public or high-load production usage

---

## Notes

This project does not store or redistribute any content.
It only processes publicly available statistics and links.

