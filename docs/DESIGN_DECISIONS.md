# Design Decisions

This document summarizes the key design decisions for the Earthquake Monitor project, covering ingestion mechanisms, database strategies, and project structure.

**Ingestion Mechanism:**
The system provides two ingestion modes: a manual endpoint for quick testing and an automatic background scheduler for continuous synchronization of earthquake data. Both use a shared internal service to avoid logic duplication and ensure consistency.


**Sync Interval:**
For real-time updates, a polling strategy is used. The interval is configurable in the code. A 5-minute interval was tested based on USGS data statistics (using `scripts/calculate_frequency.py`), but this is not a production recommendation—just a validation of a reasonable value for constant updates.


**Detection of New Events:**
The system tracks the timestamp of the last successful sync and uses it in USGS API requests to fetch only new events. This reduces data transfer volume and ensures efficient ingestion.


**Duplicate Prevention:**
Duplicate data is prevented at the database level using PostgreSQL's `ON CONFLICT DO NOTHING` mechanism, relying on each earthquake's unique identifier. Since records are not updated after publication, insertion is idempotent and safe.


**Database Schema:**
The schema includes only the essential fields from USGS events: identifier, timestamps, coordinates, depth, magnitude, magnitude type, and place description. An automatic creation timestamp is included for internal auditing.


**Index Strategy:**
Two optimized indexes were created based on query patterns:
- `idx_earthquakes_time` (BTREE): for time-range filters and ordering by date.
- `idx_earthquakes_place_gin` (GIN): for efficient text search on the `place` field.
Previous indexes on magnitude and coordinates were removed due to low relevance. The current setup focuses on performance for time filters and location search, minimizing overhead and write latency.


**Async Connection:**
The system uses SQLAlchemy's async engine with the asyncpg driver, enabling non-blocking operations and high concurrency between ingestion and API requests. Connection pooling is configured for efficient resource usage.


**Migrations and Versioning:**
Alembic is used for schema management, even with a single table. This ensures a clear history of changes, safe rollbacks, and easier future evolution of the system.


**API:**
The API is minimal, exposing endpoints to list earthquakes (with advanced filters), get details of an event, and trigger manual ingestion. This keeps the service simple and complete.


**Application Lifecycle:**
FastAPI's lifespan context manager handles the scheduler and connection cleanup, ensuring clean startup and shutdown.


**Validation and Error Handling:**
Validation is distributed: Pydantic for schemas, and constraints in the repository. For batch processing, individual record failures are logged and skipped, without failing the entire batch.


**Centralized Configuration:**
All configuration is centralized in `config.py`, loading variables from `.env`. Critical parameters like `DATABASE_URL` are validated at startup to avoid silent errors.


**Modular Structure:**
The project is modular, separating routes, models, services, repository, and configuration. This improves maintainability, supports testing, and follows FastAPI best practices.
