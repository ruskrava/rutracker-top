# Rutracker Top

FastAPI service for parsing RuTracker forums and building aggregated TOP lists
of movies based on download statistics.

The project focuses on background parsing, fast API access,
and persistent storage without using a database.

---

## What is this

Rutracker Top parses RuTracker forum sections, aggregates statistics for the same
movies across multiple topics and forums, and exposes an HTTP API to retrieve
TOP lists and detailed movie data.

The service is designed to:
- run background parsing
- survive restarts without data loss
- remain simple and transparent

---

## Current features

- Multi-forum parsing
- Global aggregation across all forums
- Topic deduplication by URL
- Background parsing using a worker thread
- Persistent cache stored on disk (`pickle`)
- Atomic cache saving
- FastAPI-based HTTP API
- Fast responses after restart
- Forum management via API

---

## API (current)

### POST /parse?url=...
Starts background parsing for a forum URL.

- Only one parsing task can run at a time
- Concurrent parse requests are ignored

---

### GET /status
Returns current service status:
- parsing state
- number of forums
- number of aggregated movies
- last parsed URL

---

### GET /top?n=10
Returns TOP-N movies by total downloads aggregated across all forums.

---

### GET /movie?title=...
Returns aggregated data for a movie:
- total downloads
- list of topics sorted by downloads

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

## Architecture

- FastAPI application
- Background parsing via `threading.Thread`
- In-memory shared data structures
- Persistent cache using `pickle`)
- Single-process design, no database

---

## Current limitations

- Single process
- Only one active parsing task at a time
- No explicit data locking
- Not intended for high-load production usage

---

## Roadmap

- Dockerfile and docker-compose support
- Scheduled background refresh
- API protection for management endpoints
- Improved input validation
- Improved error handling
- Web UI for browsing TOP lists

---

## Notes

This project does not store or redistribute any content.
It only processes publicly available statistics and links.

Internal deployment details are intentionally not included.
