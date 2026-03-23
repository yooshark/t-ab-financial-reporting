# Transaction Analytics & Financial Reporting API

A FastAPI-based financial reporting service designed to process and analyze transaction data. This project provides
analytical endpoints for transaction metrics and country-based aggregation, leveraging asynchronous database access and
Pandas for data processing.

## Core Features

- **Transaction Analytics**: `GET /api/report/` returns metrics (total, avg, min, max) with optional daily shift
  calculations (percentage change vs. the previous day).
- **Country-based Reporting**: `GET /api/report/by-country` aggregates statistics by country using external CSV data and
  Pandas.
- **Automated Data Seeding**: Automatic generation of 100+ users and 10,000+ transactions for testing and demonstration.

---

## Running the Project with Docker Compose

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yooshark/t-ab-financial-reporting.git
   cd t-ab-financial-reporting
   ```

2. **Create `.env.prod` file** (see environment variables section above or `.env.example`)

3. **Build and start all services:**
   ```bash
   docker compose up --build
   ```

---

## Local Development Setup

If you prefer to run the application without Docker:

1. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv

   # On Windows:
   .venv\Scripts\activate

   # On Linux/Mac:
   source .venv/bin/activate
   ```

2. **Install dependencies:**

   Using `uv` (recommended):
   ```bash
   uv sync
   ```

3. **Configure environment**:
   Create a `.env` file and set your local PostgreSQL credentials (see `.env.example`).

4. **Run migrations**:
   ```bash
   alembic -c app/alembic.ini upgrade head
   ```

5. **Seed the database** (optional):
   ```bash
   uv run app/db/seed.py
   ```

6. **Start the server**:
   ```bash
   uv run app/run.py
   ```

---

**Access the service:**
   - API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/api/docs` (only for DEBUG mode)

---

### Testing

Run the tests:

```bash
uv run coverage run -m pytest

uv run coverage report
```

---

### Useful Commands

```bash
# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Stop and remove volumes (clean database)
docker-compose down -v

# Rebuild specific service
docker-compose build api
```
