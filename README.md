# Earthquake Monitor

Backend system for collecting, storing and exposing earthquake data from the USGS public API.

This project retrieves earthquake events from the USGS API, stores them in a PostgreSQL database, and exposes them through a REST API built with FastAPI. A background scheduler periodically synchronizes new events, simulating real-time updates.

## Features

* Automatic ingestion of earthquake data every 10 seconds
* Manual ingestion endpoint for testing
* REST API with pagination and filtering
* PostgreSQL persistence using SQLAlchemy
* Full Docker support
* Unit and integration tests

## Technologies

* Python 3.11
* FastAPI
* SQLAlchemy 2.0
* PostgreSQL
* APScheduler
* Docker and docker-compose

## Project Structure (simplified)

```
src/
  main.py
  api/
  models/
  schemas/
  services/
  database/
  utils/

tests/
docker/
scripts/
```

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

### Docker Setup

```bash
docker-compose up --build
```

Once running, the API documentation is available at:

```
http://localhost:8000/docs
```
