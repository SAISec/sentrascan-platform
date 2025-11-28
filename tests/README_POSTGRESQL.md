# Running Security Tests with PostgreSQL

The security tests are configured to use PostgreSQL by default, matching the production database setup.

## Prerequisites

1. **Docker and Docker Compose** must be installed
2. **PostgreSQL database** must be running (via Docker Compose)

## Setup

### 1. Start PostgreSQL Database

```bash
# Start the database service
docker-compose up -d db

# Verify database is running
docker-compose ps db
```

### 2. Create Test Database

The test database (`sentrascan_test`) will be created automatically when tests run, or you can create it manually:

```bash
# Using Docker exec
docker-compose exec db psql -U sentrascan -d postgres -c "CREATE DATABASE sentrascan_test;"
```

### 3. Run Tests

Tests will automatically use PostgreSQL if `TEST_DATABASE_URL` is not set:

```bash
# Run all security tests with PostgreSQL
pytest tests/test_security.py

# Or explicitly set the database URL
TEST_DATABASE_URL="postgresql+psycopg2://sentrascan:changeme@localhost:5432/sentrascan_test" pytest tests/test_security.py
```

## Database Configuration

### Default Test Database

- **Host:** localhost
- **Port:** 5432
- **Database:** sentrascan_test
- **User:** sentrascan
- **Password:** changeme

### Override Database URL

You can override the test database URL using the `TEST_DATABASE_URL` environment variable:

```bash
# Use SQLite (fallback)
TEST_DATABASE_URL="sqlite:///:memory:" pytest tests/test_security.py

# Use different PostgreSQL database
TEST_DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/dbname" pytest tests/test_security.py
```

## Test Database Isolation

Each test function gets a fresh database session:
- Tables are created before each test
- Data is truncated (not dropped) after each test for performance
- Schema is preserved between tests

## Troubleshooting

### Database Connection Errors

If you see connection errors:

1. **Check Docker is running:**
   ```bash
   docker ps | grep postgres
   ```

2. **Check database is accessible:**
   ```bash
   docker-compose exec db psql -U sentrascan -d sentrascan_test -c "SELECT 1;"
   ```

3. **Check database exists:**
   ```bash
   docker-compose exec db psql -U sentrascan -d postgres -c "\l" | grep sentrascan_test
   ```

### Schema Creation Errors

If you see schema creation errors:

1. **Check shard_metadata schema exists:**
   ```bash
   docker-compose exec db psql -U sentrascan -d sentrascan_test -c "\dn" | grep shard_metadata
   ```

2. **Manually create schema if needed:**
   ```bash
   docker-compose exec db psql -U sentrascan -d sentrascan_test -c "CREATE SCHEMA IF NOT EXISTS shard_metadata;"
   ```

## Performance

PostgreSQL tests are slightly slower than SQLite but provide:
- ✅ Real database behavior
- ✅ Schema support (for shard_metadata)
- ✅ Production-like environment
- ✅ Better test accuracy

## CI/CD Integration

For CI/CD pipelines, ensure:
1. PostgreSQL service is available
2. `TEST_DATABASE_URL` is set appropriately
3. Database is cleaned up after tests

Example GitHub Actions:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    env:
      POSTGRES_DB: sentrascan_test
      POSTGRES_USER: sentrascan
      POSTGRES_PASSWORD: changeme
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5

env:
  TEST_DATABASE_URL: postgresql+psycopg2://sentrascan:changeme@localhost:5432/sentrascan_test
```

