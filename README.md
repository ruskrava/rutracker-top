# Rutracker Top

Service for parsing RuTracker forums and building aggregated TOP lists of movies
based on download statistics.

The project focuses on background parsing, persistent cache, and fast API access
without using a database.

## What is this

Rutracker Top parses RuTracker forum sections, aggregates statistics for the same
movies across multiple topics, and provides an API to retrieve TOP lists and
movie-related data.

The service is designed to:
- work in background
- survive restarts without losing data
- be simple to deploy and extend

## Current features

- Background parsing using worker threads
- Persistent cache stored on disk
- Automatic cache loading on startup
- Atomic cache saving after parsing
- FastAPI-based HTTP API
- No database required
- Fast responses after restart

## API (current)

POST /parse  
Starts background parsing for a forum URL.  
If parsing is already running, the request is ignored.

GET /status  
Returns current service status and number of parsed items.

GET /top?n=10  
Returns TOP-N movies by total downloads.

GET /top_v2?n=10  
Returns TOP-N movies with a link to the best topic for each movie.

## Architecture

- FastAPI application
- Background parsing in a separate thread
- Persistent cache stored on disk
- Stateless API logic
- Designed to run inside Docker with a mounted data volume

## Roadmap

Planned features and improvements:

- Support multiple forums simultaneously
- Aggregated global TOP across all forums
- Movie details endpoint (list of all topics per movie)
- Web UI for browsing TOP lists
- Background scheduled refresh
- Dockerfile and docker-compose
- Reverse proxy integration
- API protection for refresh endpoint

## Notes

This project does not store or redistribute any content.
It only processes publicly available statistics and links.

Internal deployment details (domains, proxies, infrastructure)
are intentionally not included in this repository.
