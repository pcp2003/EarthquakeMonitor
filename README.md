# Earthquake Monitor

Full-stack system for collecting, storing, and visualizing earthquake data from the USGS public API.

This project retrieves earthquake events from the USGS API, stores them in a PostgreSQL database, and exposes them through a REST API built with FastAPI. A modern Angular frontend provides an intuitive interface for viewing and filtering earthquake data. The system features both manual and automatic ingestion: a manual endpoint for quick testing and a background scheduler for continuous synchronization. The sync interval is configurable in the code. A 5-minute interval was tested based on USGS statistics, but this is not a production recommendation.

> **For detailed information about architectural and design decisions, see [docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md)**

## Features

### Backend
* Automatic ingestion of earthquake data at a configurable interval (default is 1 minute for testing)
* Manual data pull endpoint (`POST /api/v1/earthquakes/ManualSync`)
* REST API with pagination and advanced filtering (`GET /api/v1/earthquakes/list`)
* Health check endpoint (`GET /api/v1/health`)
* PostgreSQL persistence using SQLAlchemy (Async, with pooling)
* Duplicate prevention via `ON CONFLICT DO NOTHING`
* Optimized indexes: BTREE for time, GIN for text search
* Alembic for schema versioning
* Unit and integration tests (Pytest)

### Frontend
* Modern Angular 21 application
* Responsive user interface
* Real-time earthquake data visualization
* Advanced filtering capabilities
* Nginx reverse proxy for API requests
* Production-optimized build with multi-stage Docker

## Technologies

### Backend
* Python 3.11
* FastAPI
* SQLAlchemy 2.0 (Async)
* PostgreSQL
* APScheduler
* Pydantic v2
* Alembic (migrations)

### Frontend
* Angular 21
* TypeScript 5.9
* RxJS 7.8
* Nginx (for production serving)

### Infrastructure
* Docker and docker-compose
* Multi-stage Docker builds
* Nginx reverse proxy

## Project Structure

```
src/                    # Backend source code
  api/                  # API routes and dependencies
  database/             # Database connection and session management
  models/               # SQLAlchemy ORM models
  repository/           # Data access layer
  schemas/              # Pydantic schemas for validation
  services/             # Business logic (ingestion, sync, scheduler)
  main.py               # Application entry point
  config.py             # Configuration settings

frontend/               # Angular frontend application
  src/                  # Frontend source code
    app/                # Angular components and services
    index.html          # Main HTML file
    main.ts             # Application entry point
    styles.css          # Global styles
  Dockerfile            # Frontend Docker configuration
  nginx.conf            # Nginx configuration for production
  angular.json          # Angular CLI configuration
  package.json          # Node.js dependencies

tests/                  # Unit and integration tests
migrations/             # Alembic migrations
scripts/                # Utility scripts
docs/                   # Project documentation
docker-compose.yml      # Docker orchestration
Dockerfile              # Backend Docker configuration
requirements.txt        # Python dependencies
```

### Pydantic Schemas

Active schemas in `src/schemas/earthquake_schemas.py`:

- **EarthquakeBase** - Base schema with common earthquake fields
- **EarthquakeResponse** - Schema for earthquake API responses with ID and creation timestamp
- **EarthquakeListResponse** - Schema for paginated earthquake list responses
- **EarthquakeFilter** - Schema for filtering earthquake records (magnitude, depth, time range, location)
- **PaginationParams** - Schema for pagination parameters (page, limit)
- **DataRequest** - Schema for manual data synchronization requests
- **DataResponse** - Schema for data synchronization operation responses

*Unused schemas removed: `EarthquakeCreate` (no POST endpoint for earthquake creation), `HealthCheckResponse` (health endpoint returns simple dict)*

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
docker compose exec postgres psql -U earthquake_user -d earthquake_monitor
```

**Erase Database entries**
```bash
TRUNCATE TABLE table_name
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
docker compose up --build
```

3. **Access the application:**
- **Frontend (Angular)**: http://localhost:4200
- **Backend API Documentation**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000/api/v1

4. **View application logs:**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs app -f
docker compose logs frontend -f
docker compose logs postgres -f
```

5. **Run database migrations (if needed):**
```bash
docker compose exec app alembic upgrade head
```

6. **Stop all services:**
```bash
docker compose down
```

**Docker services:**
- **postgres** - PostgreSQL database (port 5432)
- **app** - FastAPI backend application (port 8000)
- **frontend** - Angular frontend with Nginx (port 4200 → 80)

**Check container health:**
```bash
docker compose ps
```

### Architecture

The application uses a three-tier architecture:

1. **Frontend (Angular + Nginx)**: 
   - Serves the Angular application on port 4200
   - Nginx reverse proxy routes `/api/*` requests to the backend
   - Production-optimized build with multi-stage Docker

2. **Backend (FastAPI)**: 
   - Exposes REST API on port 8000
   - Handles data synchronization with USGS
   - Manages database operations

3. **Database (PostgreSQL)**: 
   - Stores earthquake data on port 5432
   - Optimized indexes for performance

## API Endpoints

### Health Check
```http
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
```http
GET /api/v1/earthquakes/list?page=1&limit=20&min_magnitude=5.0
```
Returns a paginated list with optional filters:
- `min_magnitude` / `max_magnitude`
- `min_depth` / `max_depth`
- `start_time` / `end_time` (ISO 8601 format)
- `magnitude_type` (mb, ml, mw, etc)
- `place_contains` (text search)

### Get Earthquake Details
```http
GET /api/v1/earthquakes/{earthquake_id}/details
```
Returns detailed information about a specific earthquake.

### Manual Data Sync
```http
POST /api/v1/earthquakes/ManualSync
{
  "since_datetime": "2025-11-24T13:44:50.790Z"
}
```
Manually pulls earthquake data from USGS API and stores it in the database.

## Frontend Development

### Local Development (without Docker)

If you want to develop the frontend locally without Docker:

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm start
```

The frontend will be available at `http://localhost:4200` with hot-reload enabled.

**Note**: When running locally, ensure the backend is running (either via Docker or locally on port 8000) for API requests to work.

### Building for Production

```bash
cd frontend
npm run build
```

The production build will be created in `dist/frontend/browser/`.

## API Type Generation

The project automatically generates TypeScript interfaces from the backend OpenAPI specification to ensure type safety and synchronization between frontend and backend.

### Automatic Generation (CI/CD)

The GitHub Actions workflow `.github/workflows/sync-api-types.yml` automatically:
- Detects changes in backend Python files
- Generates TypeScript interfaces and Angular services
- Commits the changes if there are updates

This ensures the frontend types are always in sync with the backend API.

### Manual Generation (Local Development)

To generate types locally during development:

1. **Ensure the backend is running:**
```bash
docker compose up
```

2. **Run the generation script:**
```bash
./scripts/generate-api-types.sh
```

This will:
- Download the OpenAPI spec from `http://localhost:8000/openapi.json`
- Generate TypeScript interfaces and Angular services in `frontend/src/app/api/`
- The generated files can then be used in your Angular components

**Generated files location:** `frontend/src/app/api/`

⚠️ **Important**: Never edit the generated files manually! They will be overwritten on the next generation.
