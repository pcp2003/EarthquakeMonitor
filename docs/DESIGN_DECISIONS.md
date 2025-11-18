# Design Decisions

This document summarizes the key design decisions taken for the project, written in a simplified and natural way, covering only the relevant aspects from ingestion to project structure.

The ingestion mechanism was designed with two access modes: a manual endpoint and an automatic background task. The manual endpoint allows quick testing during development, while the periodic scheduler handles the continuous synchronization of new earthquake data. Using a shared internal ingestion service avoids duplication and keeps the logic consistent.

For real-time updates, a simple polling strategy was selected with a fixed interval of ten seconds. This approach keeps the system easy to reason about, avoids unnecessary architectural complexity, and works reliably in local and containerized environments.

To detect new earthquake events, the system tracks the timestamp of the last successful synchronization. This timestamp is passed directly to the USGS API, allowing the system to fetch only new events. This helps reduce the amount of data transferred and ensures that ingestion remains efficient.

Data duplication is prevented at the database level using PostgreSQL’s `ON CONFLICT DO NOTHING` mechanism. Each earthquake includes a unique identifier supplied by USGS, and since earthquake records are not updated after publication, it is safe to insert data in an idempotent way without worrying about overwriting existing entries.

The database schema includes only the fields necessary to represent the events from USGS: identifiers, timestamps, coordinates, depth, magnitude, magnitude type, and a human-readable place description. An automatic creation timestamp is included to support internal auditing. Indexes were created on commonly queried fields such as time, magnitude, and geographical coordinates.

The system uses asynchronous database connections through SQLAlchemy's async engine and asyncpg driver. This decision enables non-blocking I/O operations, allowing the application to handle multiple concurrent requests efficiently without thread-based overhead. Async connections are particularly beneficial for this earthquake monitoring system because it performs frequent background ingestion tasks while simultaneously serving API requests. The async approach prevents database operations from blocking the event loop, ensuring that real-time data ingestion doesn't interfere with API responsiveness, and vice versa. Connection pooling is configured with sensible defaults to manage database resources effectively across concurrent operations.

Database schema management uses Alembic for migrations, even though the current project only has a single table. This choice prioritizes version control and safety for future changes. Alembic provides a clear history of schema modifications, making it easier to track when and why changes were made. More importantly, it ensures that any future schema modifications can be applied safely with rollback capabilities if something goes wrong. While it might seem like overhead for a simple single-table project, this foundation makes the system more maintainable and reduces risks when the application needs to evolve.

The API exposes a minimal but complete set of endpoints: one for listing earthquakes with filtering capabilities, one for retrieving details of a single event, one for manually triggering ingestion, and one for health checking. This set keeps the service simple while covering all essential functionalities.

Finally, the project structure follows a modular layout, separating concerns between API routes, database models, business logic services, configuration, and utilities. This organization improves maintainability, supports testing more effectively, and aligns with common patterns used in FastAPI and modern backend applications.
