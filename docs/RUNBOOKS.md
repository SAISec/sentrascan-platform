# Operational Runbooks

Day-to-day operational procedures for SentraScan Platform.

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Health Checks](#health-checks)
3. [Incident Response](#incident-response)
4. [Maintenance Procedures](#maintenance-procedures)
5. [Emergency Procedures](#emergency-procedures)

---

## Daily Operations

### Morning Checklist

```bash
# 1. Check service status
docker-compose ps

# 2. Verify API is responding
curl http://localhost:8200/api/v1/health

# 3. Check recent scans
curl -H "X-API-Key: $API_KEY" \
  http://localhost:8200/api/v1/scans?limit=10

# 4. Review error logs
docker-compose logs --tail=100 api | grep -i error

# 5. Check database size
docker-compose exec db psql -U sentrascan -d sentrascan \
  -c "SELECT pg_size_pretty(pg_database_size('sentrascan'));"
```

### Service Status Check

```bash
#!/bin/bash
# check-status.sh

API_URL="http://localhost:8200"
API_KEY="${SENTRASCAN_API_KEY}"

echo "=== SentraScan Status Check ==="

# Health check
HEALTH=$(curl -s "$API_URL/api/v1/health")
if [ "$(echo $HEALTH | jq -r '.status')" = "ok" ]; then
    echo "✅ API Health: OK"
else
    echo "❌ API Health: FAILED"
    exit 1
fi

# Recent scans
SCANS=$(curl -s -H "X-API-Key: $API_KEY" \
  "$API_URL/api/v1/scans?limit=5")
SCAN_COUNT=$(echo $SCANS | jq 'length')
echo "📊 Recent Scans: $SCAN_COUNT"

# Failed scans
FAILED=$(echo $SCANS | jq '[.[] | select(.passed == false)] | length')
if [ "$FAILED" -gt 0 ]; then
    echo "⚠️  Failed Scans: $FAILED"
else
    echo "✅ Failed Scans: 0"
fi

# Database connection
DB_STATUS=$(docker-compose exec -T db psql -U sentrascan -d sentrascan \
  -c "SELECT 1;" 2>&1)
if echo "$DB_STATUS" | grep -q "1 row"; then
    echo "✅ Database: Connected"
else
    echo "❌ Database: Connection Failed"
    exit 1
fi
```

---

## Health Checks

### API Health Endpoint

```bash
# Basic health check
curl http://localhost:8200/api/v1/health

# Expected response:
# {"status": "ok"}
```

### Database Health

```bash
# Check database connection
docker-compose exec db psql -U sentrascan -d sentrascan \
  -c "SELECT version();"

# Check table counts
docker-compose exec db psql -U sentrascan -d sentrascan <<EOF
SELECT 
    'scans' as table_name, COUNT(*) as count FROM scans
UNION ALL
SELECT 'findings', COUNT(*) FROM findings
UNION ALL
SELECT 'baselines', COUNT(*) FROM baselines
UNION ALL
SELECT 'api_keys', COUNT(*) FROM api_keys;
EOF
```

### Scanner Health

```bash
# Check scanner availability
docker-compose exec api sentrascan doctor

# Expected output:
# ✅ modelaudit: available
# ✅ mcp-checkpoint: available
# ✅ cisco-scanner: available
```

### Resource Usage

```bash
# Check container resources
docker stats --no-stream

# Check disk usage
df -h
docker system df

# Check memory
free -h
```

---

## Incident Response

### Service Degradation

**Symptoms:**
- Slow API responses
- Timeouts
- High CPU/memory usage

**Response:**

```bash
# 1. Check service status
docker-compose ps

# 2. Check resource usage
docker stats --no-stream

# 3. Review logs
docker-compose logs --tail=200 api

# 4. Check for stuck scans
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8200/api/v1/scans?limit=100" | \
  jq '[.[] | select(.scan_status == "running")]'

# 5. Restart services if needed
docker-compose restart api

# 6. Scale if necessary
docker-compose up -d --scale api=2
```

### Database Issues

**Symptoms:**
- Connection errors
- Query timeouts
- Database lock errors

**Response:**

```bash
# 1. Check database status
docker-compose ps db

# 2. Check database logs
docker-compose logs --tail=100 db

# 3. Check connections
docker-compose exec db psql -U sentrascan -d sentrascan \
  -c "SELECT count(*) FROM pg_stat_activity;"

# 4. Check for locks
docker-compose exec db psql -U sentrascan -d sentrascan <<EOF
SELECT pid, usename, query, state, wait_event_type, wait_event
FROM pg_stat_activity
WHERE datname = 'sentrascan' AND state != 'idle';
EOF

# 5. Kill long-running queries if needed
# docker-compose exec db psql -U sentrascan -d sentrascan \
#   -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE ..."

# 6. Restart database if necessary
docker-compose restart db
```

### Scanner Failures

**Symptoms:**
- Scans failing with scanner errors
- Missing scanner dependencies
- Timeout errors

**Response:**

```bash
# 1. Check scanner availability
docker-compose exec api sentrascan doctor

# 2. Test scanner manually
docker-compose exec api mcp-checkpoint --version
docker-compose exec api mcp-scanner --version
docker-compose exec api modelaudit --version

# 3. Rebuild container if needed
docker-compose build --no-cache api
docker-compose up -d api

# 4. Check scanner logs
docker-compose logs api | grep -i scanner
```

### Authentication Issues

**Symptoms:**
- API key authentication failures
- Session expiration issues
- Permission denied errors

**Response:**

```bash
# 1. Verify API key exists
docker-compose exec api sentrascan auth list

# 2. Test API key
curl -H "X-API-Key: $API_KEY" \
  http://localhost:8200/api/v1/health

# 3. Check key status in database
docker-compose exec db psql -U sentrascan -d sentrascan \
  -c "SELECT name, role, is_revoked, created_at FROM api_keys;"

# 4. Create new key if needed
docker-compose exec api sentrascan auth create \
  --name "emergency-key" --role admin

# 5. Revoke compromised key
docker-compose exec db psql -U sentrascan -d sentrascan \
  -c "UPDATE api_keys SET is_revoked = true WHERE name = 'compromised-key';"
```

---

## Maintenance Procedures

### Database Backup

**Scheduled Backup:**

```bash
#!/bin/bash
# backup-db.sh

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/sentrascan_$TIMESTAMP.sql"

# Create backup
docker-compose exec -T db pg_dump -U sentrascan sentrascan > "$BACKUP_FILE"

# Compress
gzip "$BACKUP_FILE"

# Keep only last 30 days
find "$BACKUP_DIR" -name "sentrascan_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

**Restore from Backup:**

```bash
# 1. Stop services
docker-compose stop api

# 2. Restore database
gunzip -c backup.sql.gz | \
  docker-compose exec -T db psql -U sentrascan -d sentrascan

# 3. Verify restore
docker-compose exec db psql -U sentrascan -d sentrascan \
  -c "SELECT COUNT(*) FROM scans;"

# 4. Restart services
docker-compose start api
```

### Database Cleanup

**Remove Old Scans:**

```bash
# Remove scans older than 90 days
docker-compose exec db psql -U sentrascan -d sentrascan <<EOF
DELETE FROM scans
WHERE created_at < NOW() - INTERVAL '90 days';
EOF
```

**Vacuum Database:**

```bash
# Vacuum to reclaim space
docker-compose exec db psql -U sentrascan -d sentrascan \
  -c "VACUUM ANALYZE;"
```

### Log Rotation

```bash
# Configure log rotation in docker-compose.yml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Container Updates

```bash
# 1. Pull latest images
docker-compose pull

# 2. Backup database
./backup-db.sh

# 3. Stop services
docker-compose stop

# 4. Update containers
docker-compose up -d

# 5. Verify services
docker-compose ps
curl http://localhost:8200/api/v1/health
```

---

## Emergency Procedures

### Complete Service Failure

**Response:**

```bash
# 1. Check all services
docker-compose ps -a

# 2. Check logs
docker-compose logs --tail=200

# 3. Restart all services
docker-compose down
docker-compose up -d

# 4. Verify recovery
sleep 10
curl http://localhost:8200/api/v1/health

# 5. Check database
docker-compose exec db psql -U sentrascan -d sentrascan \
  -c "SELECT 1;"
```

### Data Corruption

**Response:**

```bash
# 1. Stop services
docker-compose stop

# 2. Restore from latest backup
gunzip -c /backups/sentrascan_latest.sql.gz | \
  docker-compose exec -T db psql -U sentrascan -d sentrascan

# 3. Verify data integrity
docker-compose exec db psql -U sentrascan -d sentrascan <<EOF
SELECT 
    COUNT(*) as scans,
    COUNT(DISTINCT scan_id) as unique_scans
FROM scans;
EOF

# 4. Restart services
docker-compose start
```

### Security Incident

**Response:**

```bash
# 1. Revoke all API keys immediately
docker-compose exec db psql -U sentrascan -d sentrascan \
  -c "UPDATE api_keys SET is_revoked = true;"

# 2. Change session secret
# Update SENTRASCAN_SECRET in docker-compose.yml
docker-compose up -d api

# 3. Review audit logs
docker-compose exec db psql -U sentrascan -d sentrascan \
  -c "SELECT * FROM scans ORDER BY created_at DESC LIMIT 100;"

# 4. Create new API keys
docker-compose exec api sentrascan auth create \
  --name "emergency-admin" --role admin

# 5. Notify security team
# Send alert with incident details
```

### Disk Space Full

**Response:**

```bash
# 1. Check disk usage
df -h
docker system df

# 2. Clean up old scans
docker-compose exec db psql -U sentrascan -d sentrascan <<EOF
DELETE FROM scans
WHERE created_at < NOW() - INTERVAL '30 days';
VACUUM;
EOF

# 3. Clean Docker
docker system prune -a --volumes

# 4. Clean old backups
find /backups -name "*.sql.gz" -mtime +7 -delete

# 5. Verify space
df -h
```

---

## Monitoring Scripts

### Health Check Script

```bash
#!/bin/bash
# health-check.sh

API_URL="${SENTRASCAN_API_URL:-http://localhost:8200}"
ALERT_EMAIL="${ALERT_EMAIL:-admin@company.com}"

check_health() {
    local status=$(curl -s "$API_URL/api/v1/health" | jq -r '.status')
    if [ "$status" != "ok" ]; then
        echo "ALERT: API health check failed"
        echo "API returned: $status"
        # Send alert
        return 1
    fi
    return 0
}

check_database() {
    local result=$(docker-compose exec -T db psql -U sentrascan -d sentrascan \
      -c "SELECT 1;" 2>&1)
    if ! echo "$result" | grep -q "1 row"; then
        echo "ALERT: Database connection failed"
        # Send alert
        return 1
    fi
    return 0
}

# Run checks
check_health || exit 1
check_database || exit 1

echo "All health checks passed"
```

### Automated Backup Script

```bash
#!/bin/bash
# auto-backup.sh

BACKUP_DIR="/backups"
RETENTION_DAYS=30

# Create backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/sentrascan_$TIMESTAMP.sql"

docker-compose exec -T db pg_dump -U sentrascan sentrascan | \
  gzip > "$BACKUP_FILE.gz"

# Verify backup
if [ -f "$BACKUP_FILE.gz" ]; then
    echo "Backup successful: $BACKUP_FILE.gz"
    
    # Remove old backups
    find "$BACKUP_DIR" -name "sentrascan_*.sql.gz" \
      -mtime +$RETENTION_DAYS -delete
    
    # Upload to S3 (optional)
    # aws s3 cp "$BACKUP_FILE.gz" s3://backups/sentrascan/
else
    echo "ERROR: Backup failed"
    exit 1
fi
```

---

## Escalation Procedures

### Severity Levels

**P0 - Critical:**
- Complete service outage
- Data loss/corruption
- Security breach

**P1 - High:**
- Service degradation
- Scanner failures
- Database issues

**P2 - Medium:**
- Performance issues
- Non-critical errors
- Feature requests

### Escalation Contacts

1. **On-Call Engineer** - First responder
2. **Team Lead** - P1+ issues
3. **Security Team** - Security incidents
4. **Database Admin** - Database issues

---

## Next Steps

**Related Guides:**
- [Monitoring Guide](MONITORING.md) - Metrics, alerting, and observability
- [Backup & Recovery](BACKUP-RECOVERY.md) - Backup and disaster recovery procedures
- [Administrator Guide](ADMIN-GUIDE.md) - Production deployment and configuration
- [Security Best Practices](SECURITY.md) - Security incident response

**Reference:**
- [Technical Documentation](TECHNICAL-DOCUMENTATION.md) - Technical details
- [Documentation Index](README.md) - Complete documentation overview

---

**Emergency Contact:** [Your on-call contact information]

