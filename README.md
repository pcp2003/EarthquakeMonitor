# Earthquake Monitor

Backend system for collecting, storing and exposing earthquake data from the USGS public API.

This project retrieves earthquake events from the USGS API, stores them in a PostgreSQL database, and exposes them through a REST API built with FastAPI. A background scheduler periodically synchronizes new events, simulating real-time updates.

> **For detailed information about architectural and design decisions, see [docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md)**

## Features

* Automatic ingestion of earthquake data every 1 minuto (configurável via .env)
* Manual data pull endpoint for testing (`POST /api/v1/earthquakes/pull`)
* REST API with pagination and filtering (`GET /api/v1/earthquakes/list`)
* Health check endpoint for monitoring (`GET /api/v1/health`)
* PostgreSQL persistence using SQLAlchemy (Async)
* Full Docker support
* Unit and integration tests (Pytest)

## Technologies

* Python 3.11
* FastAPI
* SQLAlchemy 2.0 (Async)
* PostgreSQL
* APScheduler
* Docker and docker-compose
* Pydantic v2

## Project Structure

```
src/
  api/          # API Routes and dependencies
  database/     # Database connection and session management
  models/       # SQLAlchemy ORM models
  repository/   # Data access layer
  schemas/      # Pydantic schemas for validation
  services/     # Business logic (Ingestion, Sync, Scheduler)
  main.py       # Application entry point
  config.py     # Configuration settings

tests/          # Unit and integration tests
migrations/     # Alembic migrations
scripts/        # Utility scripts
docs/           # Project documentation
```

### Pydantic Schemas

Active schemas in `src/schemas/earthquake_schemas.py`:

- **EarthquakeBase** - Base schema with common earthquake fields
- **EarthquakeResponse** - Schema for earthquake API responses with ID and creation timestamp
- **EarthquakeListResponse** - Schema for paginated earthquake list responses
- **EarthquakeFilter** - Schema for filtering earthquake records (magnitude, depth, time range, location)
- **PaginationParams** - Schema for pagination parameters (page, limit)
- **DataSyncRequest** - Schema for manual data synchronization requests
- **DataSyncResponse** - Schema for data synchronization operation responses

*Removed unused schemas: `EarthquakeCreate` (no POST endpoint for earthquake creation), `HealthCheckResponse` (health endpoint returns simple dict)*

## Database Setup

1. **Connect to PostgreSQL:**
```bash
psql postgres
```

2. **Create database and user:**
```sql
CREATE DATABASE earthquake_monitor;
CREATE USER earthquake_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE earthquake_monitor TO earthquake_user;
\q
```

3. **Set up environment variables:**
```bash
cp .env.example .env
```

4. **Edit `.env` file with your database credentials:**
```env
DATABASE_URL=postgresql+asyncpg://earthquake_user:your_password_here@localhost:5432/earthquake_monitor
```

### Database Access

**Connect to the earthquake database:**
```bash
psql -h localhost -U earthquake_user -d earthquake_monitor
```

**Common PostgreSQL commands:**
- `\l` - List all databases
- `\dt` - List all tables
- `\d table_name` - Describe table structure
- `\q` - Quit psql

## Running the Project

### Development Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up database (see Database Setup section above)**

3. **Run database migrations:**
```bash
alembic upgrade head
```

4. **Start the application:**
```bash
python src/main.py
```

### Running with Docker

1. **Ensure your `.env` file is properly configured:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

2. **Build and start all services:**
```bash
docker compose up -d
```

3. **View application logs:**
```bash
docker compose logs app -f
```

4. **Run database migrations (if needed):**
```bash
docker compose exec app alembic upgrade head
```

5. **Stop all services:**
```bash
docker compose down
```

**Docker services:**
- **postgres** - PostgreSQL database (port 5432)
  - Health check: verifica conexão a cada 5s
- **app** - Python application (port 8000)
  - Health check: verifica `/api/v1/health` a cada 30s

**Check container health:**
```bash
docker compose ps
```

### Docker Setup

```bash
docker-compose up --build
```

Once running, the API documentation is available at:

```
http://localhost:8000/docs
```

## API Endpoints

### Health Check
```bash
GET /api/v1/health
```
Checks API and database health status, returns total earthquakes and last sync time.

**Example response:**
```json
{
  "status": "healthy",
  "database": {
    "status": "connected",
    "total_earthquakes": 1852,
    "last_event_time": "2025-11-19T14:30:00"
  },
  "message": "Earthquake Monitor API is running normally"
}
```

### List Earthquakes
```bash
GET /api/v1/earthquakes/list?page=1&limit=20&min_magnitude=5.0
```
Returns paginated list with optional filters:
- `min_magnitude` / `max_magnitude`
- `min_depth` / `max_depth`
- `start_time` / `end_time` (ISO 8601 format)
- `magnitude_type` (mb, ml, mw, etc)
- `place_contains` (text search)

### Get Earthquake Details
```bash
GET /api/v1/earthquakes/{id}/details
```
Returns detailed information about a specific earthquake.

### Manual Data Pull
```bash
POST /api/v1/earthquakes/pull
{
  "since_hours": 24,
  "limit": 1000
}
```
Manually pulls earthquake data from USGS API and stores in database.
