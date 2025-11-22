# Backup & Recovery Guide

Complete guide for backing up and recovering SentraScan Platform data.

## Table of Contents

1. [Backup Strategy](#backup-strategy)
2. [Database Backup](#database-backup)
3. [File System Backup](#file-system-backup)
4. [Recovery Procedures](#recovery-procedures)
5. [Disaster Recovery](#disaster-recovery)

---

## Backup Strategy

### Backup Types

**Full Backup:**
- Complete database dump
- All configuration files
- All reports and SBOMs
- Frequency: Daily

**Incremental Backup:**
- Only changed data since last backup
- Frequency: Every 6 hours

**Point-in-Time Recovery:**
- Continuous WAL archiving
- Restore to any point in time

### Retention Policy

- **Daily backups:** 30 days
- **Weekly backups:** 12 weeks
- **Monthly backups:** 12 months
- **Yearly backups:** 7 years

---

## Database Backup

### Manual Backup

```bash
# Full backup
docker-compose exec -T db pg_dump -U sentrascan sentrascan | \
  gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup with custom format (faster restore)
docker-compose exec -T db pg_dump -U sentrascan -Fc sentrascan > \
  backup_$(date +%Y%m%d_%H%M%S).dump
```

### Automated Backup Script

```bash
#!/bin/bash
# backup-db.sh

BACKUP_DIR="/backups/database"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/sentrascan_$TIMESTAMP.sql"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Perform backup
docker-compose exec -T db pg_dump -U sentrascan sentrascan > "$BACKUP_FILE"

# Compress
gzip "$BACKUP_FILE"

# Verify backup
if [ -f "$BACKUP_FILE.gz" ]; then
    echo "✅ Backup successful: $BACKUP_FILE.gz"
    
    # Upload to S3 (optional)
    # aws s3 cp "$BACKUP_FILE.gz" s3://backups/sentrascan/database/
    
    # Remove old backups
    find "$BACKUP_DIR" -name "sentrascan_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    
    exit 0
else
    echo "❌ Backup failed"
    exit 1
fi
```

### Continuous WAL Archiving

**PostgreSQL Configuration:**

```yaml
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /backups/wal/%f && cp %p /backups/wal/%f'
```

**Backup Script:**

```bash
#!/bin/bash
# backup-wal.sh

WAL_DIR="/backups/wal"
ARCHIVE_DIR="/backups/archive"

# Archive WAL files
for wal in "$WAL_DIR"/*.wal; do
    if [ -f "$wal" ]; then
        gzip "$wal"
        mv "$wal.gz" "$ARCHIVE_DIR/"
    fi
done
```

---

## File System Backup

### Backup Script

```bash
#!/bin/bash
# backup-files.sh

BACKUP_DIR="/backups/files"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/sentrascan_files_$TIMESTAMP.tar.gz"

# Backup directories
tar -czf "$BACKUP_FILE" \
  ./data \
  ./reports \
  ./sboms \
  ./cache \
  ./.env \
  ./docker-compose.yml \
  ./nginx.conf

# Verify
if [ -f "$BACKUP_FILE" ]; then
    echo "✅ File backup successful: $BACKUP_FILE"
    # Upload to S3
    # aws s3 cp "$BACKUP_FILE" s3://backups/sentrascan/files/
else
    echo "❌ File backup failed"
    exit 1
fi
```

---

## Recovery Procedures

### Full Database Restore

```bash
# 1. Stop services
docker-compose stop api

# 2. Drop existing database (CAUTION!)
docker-compose exec db psql -U postgres -c "DROP DATABASE sentrascan;"
docker-compose exec db psql -U postgres -c "CREATE DATABASE sentrascan;"

# 3. Restore from backup
gunzip -c backup_20250120_120000.sql.gz | \
  docker-compose exec -T db psql -U sentrascan -d sentrascan

# 4. Verify restore
docker-compose exec db psql -U sentrascan -d sentrascan \
  -c "SELECT COUNT(*) FROM scans;"

# 5. Restart services
docker-compose start api
```

### Point-in-Time Recovery

```bash
# 1. Restore base backup
gunzip -c base_backup.sql.gz | \
  docker-compose exec -T db psql -U sentrascan -d sentrascan

# 2. Restore WAL files up to target time
docker-compose exec db pg_wal_restore \
  --target-time="2025-01-20 14:30:00" \
  /backups/wal/
```

### Partial Restore

```bash
# Restore specific table
docker-compose exec db psql -U sentrascan -d sentrascan <<EOF
\copy scans FROM '/backups/scans.csv' CSV HEADER;
EOF
```

---

## Disaster Recovery

### Complete System Recovery

```bash
# 1. Provision new server
# Install Docker, Docker Compose

# 2. Restore files
tar -xzf sentrascan_files_backup.tar.gz

# 3. Restore database
gunzip -c database_backup.sql.gz | \
  docker-compose exec -T db psql -U sentrascan -d sentrascan

# 4. Start services
docker-compose up -d

# 5. Verify
curl http://localhost:8200/api/v1/health
```

### RTO/RPO Targets

- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 1 hour

---

## Backup Verification

### Verify Backup Integrity

```bash
#!/bin/bash
# verify-backup.sh

BACKUP_FILE="$1"

# Check file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found"
    exit 1
fi

# Check file size
SIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null)
if [ "$SIZE" -lt 1000 ]; then
    echo "❌ Backup file too small"
    exit 1
fi

# Test restore (dry run)
gunzip -c "$BACKUP_FILE" | head -n 100 | \
  docker-compose exec -T db psql -U sentrascan -d sentrascan -f - > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Backup verification passed"
    exit 0
else
    echo "❌ Backup verification failed"
    exit 1
fi
```

---

## Automated Backup Schedule

### Cron Job

```bash
# Add to crontab
0 2 * * * /path/to/backup-db.sh >> /var/log/backup.log 2>&1
0 3 * * * /path/to/backup-files.sh >> /var/log/backup.log 2>&1
0 4 * * * /path/to/verify-backup.sh /backups/database/latest.sql.gz
```

### Systemd Timer

Create `/etc/systemd/system/sentrascan-backup.service`:

```ini
[Unit]
Description=SentraScan Backup
After=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup-db.sh
ExecStart=/usr/local/bin/backup-files.sh
```

Create `/etc/systemd/system/sentrascan-backup.timer`:

```ini
[Unit]
Description=SentraScan Backup Timer

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

---

## Cloud Backup

### AWS S3

```bash
#!/bin/bash
# backup-to-s3.sh

BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql.gz"
S3_BUCKET="sentrascan-backups"

# Create backup
docker-compose exec -T db pg_dump -U sentrascan sentrascan | gzip > "$BACKUP_FILE"

# Upload to S3
aws s3 cp "$BACKUP_FILE" "s3://$S3_BUCKET/database/"

# Enable versioning and lifecycle
aws s3api put-bucket-versioning \
  --bucket "$S3_BUCKET" \
  --versioning-configuration Status=Enabled

# Set lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket "$S3_BUCKET" \
  --lifecycle-configuration file://lifecycle.json
```

### Google Cloud Storage

```bash
# Upload to GCS
gsutil cp backup.sql.gz gs://sentrascan-backups/database/

# Set lifecycle
gsutil lifecycle set lifecycle.json gs://sentrascan-backups
```

---

## Next Steps

**Operations:**
- [Runbooks](RUNBOOKS.md) - Operational procedures including backup automation
- [Administrator Guide](ADMIN-GUIDE.md) - Production deployment
- [Monitoring Guide](MONITORING.md) - Monitoring and alerting setup

**Reference:**
- [Technical Documentation](TECHNICAL-DOCUMENTATION.md) - Technical details
- [Documentation Index](README.md) - Complete documentation overview

---

**Backup Support:** [Your backup contact]

