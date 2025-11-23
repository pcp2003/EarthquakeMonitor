# Design Decisions

This document summarizes the key design decisions taken for the project, written in a simplified and natural way, covering only the relevant aspects from ingestion to project structure.

The ingestion mechanism was designed with two access modes: a manual endpoint and an automatic background task. The manual endpoint allows quick testing during development, while the periodic scheduler handles the continuous synchronization of new earthquake data. Using a shared internal ingestion service avoids duplication and keeps the logic consistent.

For real-time updates, a polling strategy was selected with a fixed interval de 5 minutos. This decision was based on a statistical analysis of USGS data from the previous week, performed using the `scripts/calculate_frequency.py` utility. The analysis showed a total of 1,852 earthquakes, resulting in an average interval of approximately 5.44 minutes (326 seconds) between events. Setting the scheduler to 5 minutes aligns with the natural frequency of seismic events, ensuring the system remains up-to-date without making excessive requests to the external API or overloading the local database with empty checks. This approach balances data freshness with resource efficiency.

**Nevertheless, for easier visualization and testing, the configured interval in the environment is set to 1 minute. You can change the `SYNC_INTERVAL_MINUTES` variable in the `.env` file to adjust as needed.**

To detect new earthquake events, the system tracks the timestamp of the last successful synchronization. This timestamp is passed directly to the USGS API, allowing the system to fetch only new events. This helps reduce the amount of data transferred and ensures that ingestion remains efficient.

Data duplication is prevented at the database level using PostgreSQL’s `ON CONFLICT DO NOTHING` mechanism. Each earthquake includes a unique identifier, and since earthquake records are not updated after publication, it is safe to insert data in an idempotent way without worrying about overwriting existing entries.

The database schema includes only the fields necessary to represent the events from USGS: identifiers, timestamps, coordinates, depth, magnitude, magnitude type, and a human-readable place description. An automatic creation timestamp is included to support internal auditing.

**Index Strategy:** Two optimized indexes were created based on actual query patterns:
- **`idx_earthquakes_time` (BTREE)**: Supports time-range filters (`start_time`, `end_time`) and the `ORDER BY time` clause in list queries. This is the most frequently used index for fetching recent earthquakes and historical data lookups.
- **`idx_earthquakes_place_gin` (GIN)**: Uses PostgreSQL's Generalized Inverted Index for efficient full-text search on the `place` field. This optimizes the `LIKE '%place_contains%'` queries, enabling fast text matching without table scans. GIN indexes are ideal for text search operations despite slightly higher insertion overhead.

This index configuration was chosen after evaluating several strategies. Previous indexes on `magnitude` and `geographical coordinates` (latitude/longitude) were removed as they were either rarely used in isolation or never queried. The current setup provides optimal performance for the two most common query patterns: temporal filtering and location text search, while minimizing storage overhead and write latency.

The system uses asynchronous database connections through SQLAlchemy's async engine and asyncpg driver. This decision enables non-blocking I/O operations, allowing the application to handle multiple concurrent requests efficiently without thread-based overhead. Async connections are particularly beneficial for this earthquake monitoring system because it performs frequent background ingestion tasks while simultaneously serving API requests. The async approach prevents database operations from blocking the event loop, ensuring that real-time data ingestion doesn't interfere with API responsiveness, and vice versa. Connection pooling is configured with sensible defaults to manage database resources effectively across concurrent operations.

Database schema management uses Alembic for migrations, even though the current project only has a single table. This choice prioritizes version control and safety for future changes. Alembic provides a clear history of schema modifications, making it easier to track when and why changes were made. More importantly, it ensures that any future schema modifications can be applied safely with rollback capabilities if something goes wrong. While it might seem like overhead for a simple single-table project, this foundation makes the system more maintainable and reduces risks when the application needs to evolve.

The API exposes a minimal but complete set of endpoints: one for listing earthquakes with filtering capabilities, one for retrieving details of a single event, one for manually triggering ingestion. This set keeps the service simple while covering all essential functionalities.

The application lifecycle is managed using FastAPI's lifespan context manager, ensuring that the background scheduler starts automatically with the application and shuts down cleanly, along with proper database connection cleanup.

Error handling and validation are distributed across multiple layers. Pydantic schemas validate input structure at the API boundary, the ingestion service handles business logic validations, and the repository manages database constraints. When processing bulk data, individual record failures are logged and skipped rather than failing the entire batch.

Configuration is centralized in `config.py`, loading values from `.env` files. Critical settings like `DATABASE_URL` are validated at startup to fail fast if misconfigured.

Finally, the project structure follows a modular layout, separating concerns between API routes, database models, business logic services, and configuration. This organization improves maintainability, supports testing more effectively, and aligns with common patterns used in FastAPI and modern backend applications.
