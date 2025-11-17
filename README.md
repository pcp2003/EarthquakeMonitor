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

## Running the Project

```
docker-compose up --build
```

Once running, the API documentation is available at:

```
http://localhost:8000/docs
```
