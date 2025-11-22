# Administrator Guide

Production deployment and administration guide for SentraScan Platform.

## Table of Contents

1. [Production Deployment](#production-deployment)
2. [Security Hardening](#security-hardening)
3. [Performance Tuning](#performance-tuning)
4. [High Availability](#high-availability)
5. [Multi-Tenant Setup](#multi-tenant-setup)
6. [Upgrade Procedures](#upgrade-procedures)

---

## Production Deployment

### Prerequisites

- Docker 24+ and Docker Compose 2.0+
- PostgreSQL 15+ (recommended for production)
- 4GB RAM minimum (8GB recommended)
- 50GB disk space minimum
- SSL/TLS certificates (for HTTPS)

### Production docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    image: sentrascan/platform:0.1.0
    restart: unless-stopped
    command: sentrascan server --host 0.0.0.0 --port 8200
    ports:
      - "127.0.0.1:8200:8200"  # Bind to localhost only
    environment:
      - DATABASE_URL=postgresql+psycopg2://sentrascan:${DB_PASSWORD}@db:5432/sentrascan
      - SENTRASCAN_SECRET=${SENTRASCAN_SECRET}
      - SENTRASCAN_SESSION_COOKIE=ss_session
      - LOG_LEVEL=info
      - MODELAUDIT_CACHE_DIR=/cache
    depends_on:
      - db
    volumes:
      - ./data:/data
      - ./reports:/reports
      - ./sboms:/sboms
      - ./cache:/cache
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8200/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_DB=sentrascan
      - POSTGRES_USER=sentrascan
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_INITDB_ARGS=--encoding=UTF8 --locale=C
    volumes:
      - pg-data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sentrascan"]
      interval: 10s
      timeout: 5s
      retries: 5
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  pg-data:
    driver: local
```

### Environment Variables

Create `.env` file:

```bash
# Database
DB_PASSWORD=$(openssl rand -base64 32)

# Session Secret
SENTRASCAN_SECRET=$(openssl rand -base64 64)

# Optional: External services
# SENTRASCAN_ZAP_TARGETS=http://api:8200
```

### Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream sentrascan {
        server api:8200;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        listen 80;
        server_name sentrascan.example.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name sentrascan.example.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000" always;

        # API endpoints
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://sentrascan;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Web UI
        location / {
            proxy_pass http://sentrascan;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### Initial Setup

```bash
# 1. Create directories
mkdir -p data reports sboms cache backups ssl

# 2. Generate secrets
openssl rand -base64 32 > .env.db_password
openssl rand -base64 64 > .env.secret

# 3. Start services
docker-compose up -d db
sleep 10

# 4. Initialize database
docker-compose exec api sentrascan db init

# 5. Create admin API key
docker-compose exec api sentrascan auth create \
  --name "admin-production" --role admin

# 6. Start all services
docker-compose up -d

# 7. Verify
curl https://sentrascan.example.com/api/v1/health
```

---

## Security Hardening

### 1. Network Security

**Firewall Rules:**
```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable
```

**Internal Network:**
```yaml
# docker-compose.yml
services:
  api:
    networks:
      - internal
  db:
    networks:
      - internal
    # Don't expose port 5432

networks:
  internal:
    internal: true
```

### 2. Database Security

**PostgreSQL Configuration:**

```yaml
# postgresql.conf
ssl = on
ssl_cert_file = '/var/lib/postgresql/server.crt'
ssl_key_file = '/var/lib/postgresql/server.key'
password_encryption = scram-sha-256
```

**Connection Limits:**
```sql
-- Limit connections
ALTER SYSTEM SET max_connections = 100;

-- Create read-only user
CREATE USER sentrascan_readonly WITH PASSWORD 'strong-password';
GRANT CONNECT ON DATABASE sentrascan TO sentrascan_readonly;
GRANT USAGE ON SCHEMA public TO sentrascan_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO sentrascan_readonly;
```

### 3. API Security

**Rate Limiting:**
```python
# Add to server.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/mcp/scans")
@limiter.limit("10/minute")
def scan_mcp(...):
    ...
```

**CORS Configuration:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key"],
)
```

### 4. Secrets Management

**Use Secret Management:**
```yaml
# docker-compose.yml
services:
  api:
    secrets:
      - db_password
      - session_secret

secrets:
  db_password:
    external: true
  session_secret:
    external: true
```

**Docker Secrets:**
```bash
# Create secrets
echo "strong-password" | docker secret create db_password -
echo "strong-secret" | docker secret create session_secret -

# Use in docker-compose.yml
secrets:
  - source: db_password
    target: DB_PASSWORD
```

### 5. File Permissions

```bash
# Set proper permissions
chmod 600 .env
chmod 700 backups
chmod 644 ssl/*.pem
chmod 600 ssl/*.key
```

---

## Performance Tuning

### Database Optimization

**PostgreSQL Tuning:**

```sql
-- Increase shared_buffers
ALTER SYSTEM SET shared_buffers = '256MB';

-- Increase work_mem
ALTER SYSTEM SET work_mem = '16MB';

-- Enable connection pooling
-- Use pgBouncer for connection pooling
```

**Indexes:**
```sql
-- Add indexes for common queries
CREATE INDEX idx_scans_created_at ON scans(created_at DESC);
CREATE INDEX idx_scans_type_passed ON scans(scan_type, passed);
CREATE INDEX idx_findings_scan_severity ON findings(scan_id, severity);
CREATE INDEX idx_findings_severity ON findings(severity) WHERE severity IN ('CRITICAL', 'HIGH');
```

### Application Tuning

**Connection Pooling:**
```python
# In storage.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

**Caching:**
```python
# Add Redis for caching
from redis import Redis
redis_client = Redis(host='redis', port=6379, db=0)

@app.get("/api/v1/scans/{scan_id}")
@cache(expire=300)  # Cache for 5 minutes
def get_scan(scan_id: str):
    ...
```

### Resource Limits

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
  db:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## High Availability

### Load Balancing

```yaml
services:
  api:
    deploy:
      replicas: 3
    networks:
      - internal

  nginx:
    depends_on:
      - api
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
```

**Nginx Load Balancer:**
```nginx
upstream sentrascan {
    least_conn;
    server api:8200;
    server api2:8200;
    server api3:8200;
}
```

### Database Replication

**Primary-Replica Setup:**

```yaml
services:
  db-primary:
    image: postgres:15-alpine
    environment:
      - POSTGRES_REPLICATION_MODE=master
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=${REPLICATION_PASSWORD}

  db-replica:
    image: postgres:15-alpine
    environment:
      - POSTGRES_REPLICATION_MODE=slave
      - POSTGRES_MASTER_SERVICE=db-primary
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=${REPLICATION_PASSWORD}
```

### Health Checks

```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8200/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## Multi-Tenant Setup

### Organization Isolation

**Database Schema:**
```sql
ALTER TABLE scans ADD COLUMN organization_id VARCHAR;
ALTER TABLE baselines ADD COLUMN organization_id VARCHAR;
ALTER TABLE api_keys ADD COLUMN organization_id VARCHAR;

CREATE INDEX idx_scans_org ON scans(organization_id);
```

**API Middleware:**
```python
def get_organization(api_key: APIKey):
    return api_key.organization_id

@app.get("/api/v1/scans")
def list_scans(api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    org_id = get_organization(api_key)
    scans = db.query(Scan).filter(Scan.organization_id == org_id).all()
    return scans
```

---

## Upgrade Procedures

### Pre-Upgrade Checklist

```bash
# 1. Backup database
./backup-db.sh

# 2. Check current version
docker-compose exec api sentrascan --version

# 3. Review changelog
# Check for breaking changes

# 4. Test in staging
# Deploy to staging first
```

### Upgrade Steps

```bash
# 1. Stop services
docker-compose stop api

# 2. Backup
./backup-db.sh

# 3. Pull new image
docker-compose pull api

# 4. Run migrations (if any)
docker-compose run --rm api sentrascan db migrate

# 5. Start services
docker-compose up -d api

# 6. Verify
curl http://localhost:8200/api/v1/health
docker-compose exec api sentrascan doctor

# 7. Monitor logs
docker-compose logs -f api
```

### Rollback Procedure

```bash
# 1. Stop services
docker-compose stop api

# 2. Restore database (if needed)
gunzip -c backup.sql.gz | \
  docker-compose exec -T db psql -U sentrascan -d sentrascan

# 3. Use previous image
docker-compose up -d api

# 4. Verify
curl http://localhost:8200/api/v1/health
```

---

## Monitoring Setup

See [Monitoring Guide](MONITORING.md) for detailed monitoring setup.

### Quick Setup

```yaml
# Add Prometheus exporter
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

---

## Next Steps

**Operations:**
- [Runbooks](RUNBOOKS.md) - Day-to-day operational procedures
- [Monitoring Guide](MONITORING.md) - Metrics, alerting, and observability
- [Backup & Recovery](BACKUP-RECOVERY.md) - Backup and disaster recovery procedures

**Security:**
- [Security Best Practices](SECURITY.md) - Security hardening and compliance

**Reference:**
- [Technical Documentation](TECHNICAL-DOCUMENTATION.md) - Complete technical reference
- [Documentation Index](README.md) - Complete documentation overview

---

**Production Support:** [Your support contact]

