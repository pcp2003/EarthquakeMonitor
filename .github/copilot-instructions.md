# GitHub Copilot Custom Instructions - Earthquake Monitor

## Project Overview
Full-stack earthquake monitoring system that collects, stores, and visualizes real-time earthquake data from the USGS public API. The system features automatic data synchronization, REST API endpoints, and a modern Angular frontend for intuitive data visualization and filtering.

**Key Purpose**: Provide a reliable, scalable solution for monitoring and analyzing earthquake events with configurable ingestion intervals and comprehensive filtering capabilities.

## Tech Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 (Async with connection pooling)
- **Database**: PostgreSQL 15+
- **Scheduler**: APScheduler (for automatic data sync)
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Testing**: Pytest
- **ASGI Server**: Uvicorn

### Frontend
- **Framework**: Angular 21
- **Language**: TypeScript 5.9
- **State Management**: RxJS 7.8
- **HTTP Client**: Angular HttpClient
- **Build Tool**: Angular CLI
- **Production Server**: Nginx

### Infrastructure
- **Containerization**: Docker, docker-compose
- **Reverse Proxy**: Nginx (for API routing in frontend)
- **CI/CD**: GitHub Actions (API type generation)

## Project Structure
```
earthquake-monitor/
├── src/                      # Backend source code
│   ├── api/                  # FastAPI routes and dependencies
│   ├── database/             # Database connection and session management
│   ├── models/               # SQLAlchemy ORM models
│   ├── repository/           # Data access layer (repository pattern)
│   ├── schemas/              # Pydantic schemas for validation
│   ├── services/             # Business logic (ingestion, sync, scheduler)
│   ├── main.py               # Application entry point
│   └── config.py             # Configuration settings (from .env)
├── frontend/                 # Angular frontend application
│   ├── src/
│   │   ├── app/
│   │   │   ├── api/          # Auto-generated TypeScript interfaces
│   │   │   ├── components/   # Angular components
│   │   │   ├── services/     # Angular services
│   │   │   └── models/       # TypeScript interfaces
│   │   ├── index.html
│   │   ├── main.ts
│   │   └── styles.css
│   ├── Dockerfile            # Multi-stage Docker build
│   ├── nginx.conf            # Nginx reverse proxy config
│   └── angular.json
├── tests/                    # Pytest unit and integration tests
├── migrations/               # Alembic database migrations
├── scripts/                  # Utility scripts (API type generation)
├── docs/                     # Project documentation
│   └── DESIGN_DECISIONS.md   # Architectural decisions
├── .github/workflows/        # GitHub Actions CI/CD
├── docker-compose.yml        # Multi-service orchestration
├── Dockerfile                # Backend Docker configuration
├── requirements.txt          # Python dependencies
└── .env.example              # Environment variables template
```

## Code Conventions

### Python (Backend)
- **Style Guide**: Strictly follow PEP 8
- **Line Length**: Maximum 100 characters
- **Type Hints**: Required for all function signatures and class attributes
- **Imports**: Organized with `isort` (stdlib → third-party → local)
- **Docstrings**: Google style for all public functions and classes
- **Async/Await**: Use async for all I/O operations (database, HTTP)
- **Error Handling**: Use custom exception classes, always log with context

#### Naming Conventions
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private Methods**: `_leading_underscore`
- **Async Functions**: Prefix with `async def`, no special naming

#### FastAPI Specific
- **Route Decorators**: Use explicit HTTP methods (`@router.get`, `@router.post`)
- **Dependencies**: Use `Depends()` for dependency injection
- **Response Models**: Always specify `response_model` in decorators
- **Status Codes**: Use `status.HTTP_*` constants from `fastapi`
- **Path Parameters**: Use type hints (`earthquake_id: str`)

#### SQLAlchemy (Async)
- **Session Management**: Always use `async with` context managers
- **Queries**: Use `select()` construct, avoid legacy query API
- **Transactions**: Commit explicitly, handle rollbacks in except blocks
- **Models**: Inherit from `Base`, use `Mapped` type hints
- **Relationships**: Define bidirectional with `back_populates`

### TypeScript/Angular (Frontend)
- **Style**: Follow Angular style guide
- **Semicolons**: Always use
- **Quotes**: Single quotes for strings
- **Type Safety**: Enable `strict` mode in `tsconfig.json`
- **Naming**:
  - Components: `PascalCase` + `Component` suffix
  - Services: `PascalCase` + `Service` suffix
  - Interfaces: `PascalCase` (no `I` prefix)
  - Files: `kebab-case.component.ts`

#### Angular Specific
- **Components**: Use standalone components (Angular 14+)
- **Services**: Provide in root with `providedIn: 'root'`
- **Observables**: Use RxJS operators, avoid nested subscriptions
- **HTTP**: Use typed responses with interfaces
- **Templates**: Use `@if` and `@for` (Angular 17+ syntax)
- **Change Detection**: Use `OnPush` strategy when possible

### API Type Generation
- **NEVER** manually edit files in `frontend/src/app/api/`
- These files are auto-generated from OpenAPI spec
- Run `./scripts/generate-api-types.sh` after backend schema changes
- CI/CD automatically regenerates on backend changes

## Architecture Patterns

### Backend (Repository Pattern)
```
Controller (API) → Service → Repository → Database
```
- **API Layer**: Handle HTTP, validation, serialization
- **Service Layer**: Business logic, orchestration
- **Repository Layer**: Data access, queries
- **Never** skip layers (e.g., no direct DB access from API)

### Database Optimization
- **Indexes**: 
  - BTREE for time-based queries (`event_time`)
  - GIN for full-text search (`place`)
- **Duplicate Prevention**: `ON CONFLICT DO NOTHING` on `usgs_id`
- **Connection Pooling**: Configured in SQLAlchemy (max 20 connections)
- **Async Operations**: All database calls are non-blocking

### Data Synchronization
- **Automatic**: APScheduler runs every 1 minute (configurable)
- **Manual**: `POST /api/v1/earthquakes/ManualSync` endpoint
- **Idempotency**: Duplicate detection via unique constraints
- **Error Recovery**: Retries on transient failures, logs on permanent failures

## Testing Standards

### Unit Tests (Pytest)
- **Coverage**: Minimum 80% for new code
- **Location**: `tests/` directory mirrors `src/` structure
- **Fixtures**: Use pytest fixtures for common setup (DB, client)
- **Mocking**: Mock external APIs (USGS), use real DB for integration tests
- **Async Tests**: Use `pytest-asyncio` decorator

### Test Naming
```python
def test_<function_name>_should_<expected_behavior>_when_<condition>():
    # Arrange
    # Act
    # Assert
```

### Example Test Structure
```python
@pytest.mark.asyncio
async def test_create_earthquake_should_return_earthquake_when_valid_data():
    # Arrange
    async with AsyncSessionLocal() as session:
        repo = EarthquakeRepository(session)
        data = EarthquakeCreate(usgs_id="test123", magnitude=5.0, ...)
        
        # Act
        result = await repo.create(data)
        
        # Assert
        assert result.usgs_id == "test123"
        assert result.magnitude == 5.0
```

## API Design Principles

### REST Conventions
- **List**: `GET /api/v1/earthquakes/list` (with pagination)
- **Detail**: `GET /api/v1/earthquakes/{id}/details`
- **Create**: Not exposed (data from USGS only)
- **Update/Delete**: Not exposed (immutable earthquake data)
- **Actions**: `POST /api/v1/earthquakes/ManualSync`

### Response Format
```json
{
  "items": [...],
  "total": 1852,
  "page": 1,
  "limit": 20,
  "pages": 93
}
```

### Error Responses
```json
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## Environment Configuration

### Required Environment Variables (.env)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/earthquake_monitor
USGS_API_URL=https://earthquake.usgs.gov/fdsnws/event/1/query
SYNC_INTERVAL_MINUTES=1
LOG_LEVEL=INFO
```

### Configuration Loading
- Use `python-dotenv` for .env file loading
- Validate all required variables on startup
- Use Pydantic `Settings` class for type safety

## Security Best Practices

### Backend
- **Input Validation**: All inputs validated with Pydantic schemas
- **SQL Injection**: Prevented by SQLAlchemy ORM
- **CORS**: Configured for frontend origin only
- **Rate Limiting**: Consider adding for production (not implemented)
- **Secrets**: Never commit `.env` file, use `.env.example` template

### Frontend
- **XSS Prevention**: Angular sanitizes templates automatically
- **CSRF**: Not applicable (API is stateless, no cookies)
- **API Keys**: None required (USGS API is public)

### Docker
- **Non-root User**: Containers run as non-root
- **Multi-stage Builds**: Minimize image size and attack surface
- **Network Isolation**: Services communicate via Docker network

## Docker Best Practices

### Development Workflow
```bash
# Start all services
docker compose up --build

# View logs
docker compose logs -f app

# Run migrations
docker compose exec app alembic upgrade head

# Access database
docker compose exec postgres psql -U earthquake_user -d earthquake_monitor

# Stop services
docker compose down
```

### Service Ports
- **Frontend**: 4200 (Nginx serves Angular on port 80 internally)
- **Backend**: 8000 (FastAPI)
- **Database**: 5432 (PostgreSQL)

### Volume Mounts
- Database data persisted in Docker volume
- Backend code mounted for development hot-reload

## Git Workflow

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `hotfix/*` - Critical production fixes

### Commit Messages (Conventional Commits)
```
feat(backend): add earthquake depth filtering
fix(frontend): resolve pagination bug on list page
docs: update API documentation
refactor(repository): simplify query builder
test(services): add tests for sync service
chore(deps): update Angular to version 21
```

### Pull Request Checklist
- [ ] Tests pass (`pytest`)
- [ ] Code coverage meets 80% threshold
- [ ] API types regenerated (if backend changed)
- [ ] Documentation updated
- [ ] No console.log or print statements
- [ ] Docker build succeeds

## Database Management

### Migrations (Alembic)
```bash
# Create new migration
alembic revision --autogenerate -m "add magnitude index"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Common PostgreSQL Commands
```sql
-- Check table structure
\d earthquakes

-- Count records
SELECT COUNT(*) FROM earthquakes;

-- View recent earthquakes
SELECT * FROM earthquakes ORDER BY event_time DESC LIMIT 10;

-- Truncate table (development only)
TRUNCATE TABLE earthquakes;
```

## Performance Optimization

### Backend
- **Async I/O**: All database and HTTP calls are async
- **Connection Pooling**: SQLAlchemy pool (max 20 connections)
- **Pagination**: Always paginate list endpoints (default 20 items)
- **Indexes**: Optimized for common queries (time, magnitude, location)
- **Batch Operations**: Use bulk inserts for data sync

### Frontend
- **Lazy Loading**: Modules loaded on demand
- **OnPush Strategy**: Reduce change detection cycles
- **TrackBy**: Use with *ngFor for performance
- **Debounce**: Debounce search inputs (300ms)
- **HTTP Caching**: Cache GET requests where appropriate

### Database
- **Index Usage**: Monitor with `EXPLAIN ANALYZE`
- **Query Optimization**: Avoid N+1 queries
- **Batch Inserts**: Use `executemany` for bulk operations

## Monitoring and Logging

### Logging Standards
```python
# Backend (Python logging)
logger.info("Syncing earthquakes", extra={"since": since_datetime})
logger.error("Failed to sync data", exc_info=True, extra={"error": str(e)})
```

### Health Check
```http
GET /api/v1/health
```
Returns:
- API status
- Database connection status
- Total earthquake count
- Last sync timestamp

## Documentation

### Code Comments
- Comment **WHY**, not **WHAT**
- Document complex algorithms and business logic
- Keep comments synchronized with code changes

### Docstring Example (Python)
```python
async def sync_earthquakes(since_datetime: datetime) -> int:
    """
    Synchronizes earthquake data from USGS API.
    
    Fetches earthquakes that occurred after the specified datetime
    and stores them in the database, skipping duplicates.
    
    Args:
        since_datetime: Only fetch earthquakes after this time
        
    Returns:
        Number of new earthquakes added to the database
        
    Raises:
        USGSAPIError: If the USGS API request fails
        DatabaseError: If database operation fails
        
    Example:
        >>> count = await sync_earthquakes(datetime(2025, 1, 1))
        >>> print(f"Added {count} earthquakes")
    """
```

### TypeScript Comments (Angular)
```typescript
/**
 * Fetches filtered earthquake list from API
 * 
 * @param filters - Optional filters for magnitude, depth, time range
 * @param page - Page number (1-indexed)
 * @param limit - Items per page
 * @returns Observable of paginated earthquake response
 */
getEarthquakes(filters?: EarthquakeFilter, page = 1, limit = 20): Observable<EarthquakeListResponse> {
  // implementation
}
```

## Rules and Boundaries

### ✅ ALWAYS DO
- Write tests for all new features and bug fixes
- Use type hints in Python, strict types in TypeScript
- Validate all API inputs with Pydantic schemas
- Use async/await for I/O operations
- Log errors with context (user ID, request ID, etc.)
- Run `./scripts/generate-api-types.sh` after backend schema changes
- Update documentation when changing API contracts
- Use dependency injection in FastAPI
- Handle errors gracefully with user-friendly messages
- Check health endpoint before deploying

### ⚠️ ASK BEFORE
- Changing database schema (coordinate migration)
- Adding new Python or npm dependencies
- Modifying USGS API request parameters
- Changing sync interval timing
- Altering Docker network configuration
- Adding new API endpoints (discuss design first)
- Modifying Nginx reverse proxy rules

### ❌ NEVER DO
- Edit files in `frontend/src/app/api/` manually (auto-generated)
- Commit `.env` file or secrets to git
- Use `print()` in Python code (use `logger` instead)
- Use `console.log()` in production TypeScript
- Skip input validation on API endpoints
- Use synchronous I/O in backend (no `requests`, use `httpx`)
- Commit commented-out code
- Use `any` type in TypeScript
- Push directly to `main` branch
- Modify migration files after they're applied
- Use root user in Docker containers

## External APIs

### USGS Earthquake API
- **Base URL**: https://earthquake.usgs.gov/fdsnws/event/1/query
- **Format**: GeoJSON
- **Rate Limit**: None documented, but be respectful
- **Default Query**: Last 30 days, magnitude 2.5+
- **Documentation**: https://earthquake.usgs.gov/fdsnws/event/1/

### Request Example
```python
params = {
    "format": "geojson",
    "starttime": "2025-01-01",
    "minmagnitude": 2.5,
}
```

## CI/CD Pipeline

### GitHub Actions Workflows
1. **API Type Generation** (`.github/workflows/sync-api-types.yml`)
   - Triggers on Python file changes in `src/`
   - Generates TypeScript interfaces from OpenAPI spec
   - Auto-commits generated files

### Future CI/CD (Not Implemented)
- Run pytest on PRs
- Build Docker images
- Deploy to staging/production
- Run integration tests

## Development Workflow

### Starting a New Feature
1. Create feature branch: `git checkout -b feature/earthquake-alerts`
2. Implement backend changes with tests
3. Update Pydantic schemas if API changes
4. Run API type generation: `./scripts/generate-api-types.sh`
5. Implement frontend changes
6. Test locally with Docker: `docker compose up --build`
7. Commit with conventional commit message
8. Create pull request to `develop`

### Local Development (Without Docker)
1. Set up Python virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Start PostgreSQL locally
4. Run migrations: `alembic upgrade head`
5. Start backend: `python src/main.py`
6. Start frontend: `cd frontend && npm start`

## Troubleshooting

### Common Issues
- **Database connection fails**: Check DATABASE_URL in .env
- **Port already in use**: Stop existing services or change ports
- **Migration conflicts**: Reset database and rerun migrations
- **API types out of sync**: Run `./scripts/generate-api-types.sh`
- **Docker build fails**: Clear cache with `docker compose build --no-cache`

## Resources

### Internal Documentation
- `/docs/DESIGN_DECISIONS.md` - Architectural decisions and rationale
- `/README.md` - Project overview and setup instructions
- FastAPI Docs: http://localhost:8000/docs (when running)

### External Documentation
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Angular](https://angular.dev/)
- [Pydantic](https://docs.pydantic.dev/)
- [USGS API](https://earthquake.usgs.gov/fdsnws/event/1/)

## Notes for Copilot

### Project Philosophy
- **Reliability**: System must handle API failures gracefully
- **Data Integrity**: Prevent duplicates, maintain consistency
- **Performance**: Optimize for read-heavy workload
- **Simplicity**: Prefer simple, testable solutions
- **Type Safety**: Leverage Python type hints and TypeScript strict mode

### When Suggesting Code
1. **Understand the layer**: API, Service, Repository, or Model
2. **Follow async patterns**: All I/O must be async
3. **Include error handling**: Try-except with logging
4. **Add type hints**: Required for all functions
5. **Write tests first**: TDD approach preferred
6. **Consider performance**: Pagination, indexing, caching
7. **Document complex logic**: Why, not what

### Context Awareness
- This is a **data ingestion and visualization system**
- Data source is **external and immutable** (USGS API)
- Users **only read data**, no create/update/delete
- **Automatic sync** runs continuously in background
- **High read volume** expected, optimize queries

---

**Last updated**: December 2025
**Version**: 1.0.0
**Python**: 3.11+ | **Angular**: 21 | **PostgreSQL**: 15+