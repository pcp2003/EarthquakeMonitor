#!/bin/bash
set -e

echo "Starting Earthquake Monitor application..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h postgres -p 5432 -U ${DB_USER}; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - executing migrations"

# Run Alembic migrations
alembic upgrade head

echo "Migrations completed successfully"

# Start the application
echo "Starting FastAPI application..."
exec python src/main.py
