# Breaking Changes and Migration Guide

**Document Version:** 1.0  
**Date:** 2025-11-28  
**Platform Version:** Enhanced Platform (Post-PRD Implementation)

---

## Overview

This document outlines breaking changes introduced in the SentraScan Platform Enhancements and provides migration guidance for existing deployments.

---

## Summary of Breaking Changes

### Critical Breaking Changes

1. **Database Schema Changes** - Multi-tenancy support requires schema migration
2. **API Key Format Change** - New API key format (`ss-proj-h_` prefix)
3. **Authentication Changes** - User-based authentication replaces API-key-only auth
4. **Database Backend** - PostgreSQL recommended (SQLite still supported but limited)
5. **Container Protection** - Production containers require build-time key

### Non-Breaking Changes (Backward Compatible)

1. **Logging Format** - JSON logging (old format still readable)
2. **UI Updates** - UI enhancements (backward compatible)
3. **Analytics** - New analytics endpoints (additive)

---

## Detailed Breaking Changes

### 1. Database Schema Changes

#### 1.1 Multi-Tenancy Schema

**Impact:** HIGH - Requires database migration

**Changes:**
- New `tenants` table
- New `users` table
- New `tenant_settings` table
- New `audit_logs` table
- Added `tenant_id` column to: `scans`, `findings`, `api_keys`, `baselines`, `sboms`
- New `shard_metadata` schema for database sharding

**Migration Steps:**

1. **Backup existing database:**
```bash
# SQLite
cp sentrascan.db sentrascan.db.backup

# PostgreSQL
pg_dump -U sentrascan sentrascan > sentrascan_backup.sql
```

2. **Run migration script:**
```bash
python -m sentrascan.cli migrate
```

3. **Verify migration:**
```bash
python -m sentrascan.cli verify-migration
```

**Rollback:**
- Restore from backup
- Use previous version of application

**Affected Components:**
- All database queries must include `tenant_id` filter
- API endpoints require tenant context
- Database sharding (if enabled)

---

### 2. API Key Format Change

#### 2.1 New API Key Format

**Impact:** MEDIUM - Existing API keys remain valid, new keys use new format

**Old Format:**
- Variable length alphanumeric string
- No specific prefix

**New Format:**
- Prefix: `ss-proj-h_`
- 147-character alphanumeric string with exactly one hyphen
- Total length: 157 characters

**Migration Steps:**

1. **Existing API keys:**
   - Old API keys continue to work
   - No migration required for existing keys
   - New keys generated use new format

2. **Update API key validation:**
   - If you have custom validation, update to accept both formats
   - New format validation: `^ss-proj-h_[A-Za-z0-9-]{147}$`

**Affected Components:**
- API key generation (`generate_api_key()`)
- API key validation (`validate_api_key_format()`)
- API key storage (format stored in database)

---

### 3. Authentication Changes

#### 3.1 User-Based Authentication

**Impact:** HIGH - New authentication system

**Changes:**
- User-based authentication with email/password
- Session management with secure cookies
- MFA support (optional)
- Account lockout after failed attempts
- Password policies (min 12 chars, complexity)

**Migration Steps:**

1. **Create default tenant:**
```bash
python -m sentrascan.cli create-tenant --name "Default Tenant"
```

2. **Create admin user:**
```bash
python -m sentrascan.cli create-user \
  --email admin@example.com \
  --password "SecurePassword123!" \
  --role super_admin \
  --tenant-id <tenant-id>
```

3. **Migrate existing API keys:**
   - Existing API keys are associated with default tenant
   - API keys can be assigned to users

**Rollback:**
- Use API key authentication (still supported)
- Disable user authentication in configuration

**Affected Components:**
- Login endpoints (`/login`, `/register`)
- Session management
- User management endpoints
- RBAC enforcement

---

### 4. Database Backend Changes

#### 4.1 PostgreSQL Recommended

**Impact:** MEDIUM - SQLite still supported but with limitations

**Changes:**
- PostgreSQL recommended for production
- SQLite supported for development/testing
- Database sharding requires PostgreSQL
- Encryption at rest requires PostgreSQL

**Migration Steps:**

1. **Install PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

2. **Create database:**
```bash
createdb sentrascan
```

3. **Update configuration:**
```bash
export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/sentrascan"
```

4. **Run migrations:**
```bash
python -m sentrascan.cli migrate
```

**Rollback:**
- Switch back to SQLite (if not using sharding/encryption)
- Update `DATABASE_URL` environment variable

**Affected Components:**
- Database connection (`src/sentrascan/core/storage.py`)
- Schema-based sharding
- Encryption at rest

---

### 5. Container Protection

#### 5.1 Build-Time Key Required

**Impact:** MEDIUM - Production containers require key

**Changes:**
- Production containers require `CONTAINER_ACCESS_KEY` at build time
- Key cannot be changed at runtime
- Protected containers cannot be accessed without key

**Migration Steps:**

1. **Set build-time key:**
```bash
export CONTAINER_ACCESS_KEY="your-secure-key-here"
docker build --build-arg CONTAINER_ACCESS_KEY="$CONTAINER_ACCESS_KEY" \
  -t sentrascan:protected -f Dockerfile.protected .
```

2. **Use protected container:**
```bash
docker run -e CONTAINER_ACCESS_KEY="your-secure-key-here" sentrascan:protected
```

**Rollback:**
- Use standard container (`Dockerfile.production`)
- Remove `CONTAINER_ACCESS_KEY` requirement

**Affected Components:**
- Container build process
- Container startup
- Container access control

---

## Non-Breaking Changes

### 1. Logging Format

**Impact:** LOW - Backward compatible

**Changes:**
- JSON-structured logging (OTEL compliant)
- Old log format still readable
- Log masking for sensitive data

**Migration Steps:**
- No migration required
- Update log parsers to handle JSON format (optional)

---

### 2. UI Updates

**Impact:** LOW - Backward compatible

**Changes:**
- Modern UI design
- Footer copyright update
- Statistics cards layout
- Findings display enhancements

**Migration Steps:**
- No migration required
- UI updates are additive

---

### 3. Analytics Endpoints

**Impact:** LOW - Additive features

**Changes:**
- New analytics endpoints (`/api/analytics/*`)
- ML insights endpoints
- Tenant-scoped analytics

**Migration Steps:**
- No migration required
- New endpoints are optional

---

## Migration Checklist

### Pre-Migration

- [ ] Backup existing database
- [ ] Backup configuration files
- [ ] Review breaking changes
- [ ] Test migration in staging environment
- [ ] Prepare rollback plan

### Migration Steps

- [ ] Install/upgrade to new version
- [ ] Run database migrations
- [ ] Create default tenant
- [ ] Create admin user
- [ ] Migrate existing API keys
- [ ] Update configuration
- [ ] Test authentication
- [ ] Verify data integrity
- [ ] Test API endpoints
- [ ] Test UI functionality

### Post-Migration

- [ ] Verify all features work
- [ ] Monitor logs for errors
- [ ] Update documentation
- [ ] Notify users of changes
- [ ] Remove old backups (after verification)

---

## Rollback Procedures

### Database Rollback

1. **Stop application:**
```bash
docker-compose down
```

2. **Restore database:**
```bash
# SQLite
cp sentrascan.db.backup sentrascan.db

# PostgreSQL
psql -U sentrascan sentrascan < sentrascan_backup.sql
```

3. **Revert to previous version:**
```bash
git checkout <previous-version>
docker-compose up -d
```

### Configuration Rollback

1. **Restore configuration:**
```bash
cp config.yaml.backup config.yaml
```

2. **Restart application:**
```bash
docker-compose restart
```

---

## Compatibility Matrix

| Feature | Old Version | New Version | Migration Required |
|---------|-------------|-------------|-------------------|
| Database Schema | Single-tenant | Multi-tenant | ✅ Yes |
| API Key Format | Variable | `ss-proj-h_` prefix | ⚠️ Partial (new keys only) |
| Authentication | API key only | User + API key | ✅ Yes |
| Database Backend | SQLite | PostgreSQL (recommended) | ⚠️ Optional |
| Container Protection | None | Build-time key | ⚠️ Optional |
| Logging Format | Plain text | JSON | ❌ No |
| UI | Basic | Enhanced | ❌ No |
| Analytics | None | Full analytics | ❌ No |

---

## Support and Resources

### Documentation

- [Migration Guide](./MIGRATION_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Configuration Guide](./CONFIGURATION_GUIDE.md)

### Support Channels

- GitHub Issues: [Report Issues](https://github.com/sentrascan/platform/issues)
- Documentation: [Full Documentation](./README.md)

---

## Version History

### Version 1.0 (2025-11-28)
- Initial breaking changes documentation
- Multi-tenancy migration guide
- Authentication migration guide
- Database migration guide

---

**Last Updated:** 2025-11-28  
**Maintained By:** SentraScan Platform Team

