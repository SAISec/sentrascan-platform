# Security Best Practices

Comprehensive security guide for SentraScan Platform.

## Table of Contents

1. [Security Checklist](#security-checklist)
2. [Network Security](#network-security)
3. [Application Security](#application-security)
4. [Data Security](#data-security)
5. [Compliance](#compliance)

---

## Security Checklist

### Pre-Deployment

- [ ] Change all default passwords
- [ ] Generate strong secrets (64+ characters)
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Configure backup encryption
- [ ] Review file permissions
- [ ] Disable unnecessary services
- [ ] Update all dependencies

### Post-Deployment

- [ ] Verify HTTPS is working
- [ ] Test authentication
- [ ] Review access logs
- [ ] Set up monitoring
- [ ] Configure alerts
- [ ] Test backup/restore
- [ ] Review security headers
- [ ] Verify database encryption
- [ ] Test rate limiting
- [ ] Review API key management

---

## Network Security

### Firewall Configuration

```bash
# Allow only necessary ports
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp   # HTTP (redirect to HTTPS)
ufw allow 443/tcp  # HTTPS
ufw enable
```

### Internal Network Isolation

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
    driver: bridge
```

### DDoS Protection

```nginx
# nginx.conf
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;

server {
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
    }
    
    location /login {
        limit_req zone=login_limit burst=3 nodelay;
    }
}
```

---

## Application Security

### Authentication

**Strong API Keys:**
```python
import secrets
import hashlib

# Generate strong key
api_key = secrets.token_urlsafe(32)  # 256 bits

# Hash before storage
key_hash = hashlib.sha256(api_key.encode()).hexdigest()
```

**Session Security:**
```python
# Use strong secret (64+ characters)
SECRET = os.environ.get("SENTRASCAN_SECRET")
if len(SECRET) < 64:
    raise ValueError("SENTRASCAN_SECRET must be at least 64 characters")

# Set secure cookie flags
response.set_cookie(
    SESSION_COOKIE,
    sign(api_key),
    httponly=True,
    secure=True,  # HTTPS only
    samesite="strict",
    max_age=3600  # 1 hour
)
```

### Input Validation

```python
from pydantic import BaseModel, validator

class ScanRequest(BaseModel):
    config_paths: List[str]
    auto_discover: bool = False
    
    @validator('config_paths')
    def validate_paths(cls, v):
        # Prevent path traversal
        for path in v:
            if '..' in path or path.startswith('/'):
                raise ValueError("Invalid path")
        return v
```

### SQL Injection Prevention

```python
# Use parameterized queries
from sqlalchemy import text

# ❌ Bad
query = f"SELECT * FROM scans WHERE id = '{scan_id}'"

# ✅ Good
query = text("SELECT * FROM scans WHERE id = :id")
result = db.execute(query, {"id": scan_id})
```

### XSS Prevention

```python
from markupsafe import escape

# Escape user input
user_input = escape(user_input)

# Use Jinja2 auto-escaping
# In templates, {{ variable }} is auto-escaped
```

---

## Data Security

### Encryption at Rest

**Database Encryption:**

```yaml
# PostgreSQL with encryption
services:
  db:
    environment:
      - POSTGRES_INITDB_ARGS=--encoding=UTF8 --locale=C
    volumes:
      - encrypted-data:/var/lib/postgresql/data

volumes:
  encrypted-data:
    driver: local
    driver_opts:
      type: crypt
      device: /dev/sdb1
```

**File Encryption:**

```bash
# Encrypt backup files
gpg --symmetric --cipher-algo AES256 backup.sql.gz

# Decrypt
gpg --decrypt backup.sql.gz.gpg > backup.sql.gz
```

### Encryption in Transit

**TLS Configuration:**

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

### Secrets Management

**Never commit secrets:**
```bash
# ❌ Bad
echo "API_KEY=sk-123456" >> .env
git add .env

# ✅ Good
echo "API_KEY=sk-123456" >> .env
echo ".env" >> .gitignore
```

**Use secret management:**
```yaml
# Docker secrets
secrets:
  db_password:
    external: true
  api_secret:
    external: true
```

---

## Compliance

### SOC 2

**Requirements:**
- Access controls
- Audit logging
- Encryption
- Incident response

**Implementation:**
```python
# Audit logging
import logging

audit_logger = logging.getLogger('audit')

def audit_log(action, user, resource, details):
    audit_logger.info(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "user": user,
        "resource": resource,
        "details": details
    }))
```

### GDPR

**Data Protection:**
- Encrypt personal data
- Implement data retention policies
- Provide data export
- Support data deletion

**Implementation:**
```python
@app.post("/api/v1/data/export")
def export_user_data(user_id: str, db: Session = Depends(get_db)):
    # Export all user data
    data = {
        "scans": db.query(Scan).filter(Scan.created_by == user_id).all(),
        "api_keys": db.query(APIKey).filter(APIKey.created_by == user_id).all()
    }
    return data

@app.delete("/api/v1/data/delete")
def delete_user_data(user_id: str, db: Session = Depends(get_db)):
    # Delete all user data
    db.query(Scan).filter(Scan.created_by == user_id).delete()
    db.query(APIKey).filter(APIKey.created_by == user_id).delete()
    db.commit()
```

### ISO 27001

**Security Controls:**
- Access control
- Cryptography
- Operations security
- Incident management

---

## Vulnerability Management

### Dependency Scanning

```bash
# Scan dependencies
pip install safety
safety check

# Use Dependabot/GitHub Security
# Automatically scan and update dependencies
```

### Container Scanning

```bash
# Scan Docker images
docker scan sentrascan/platform:latest

# Use Trivy
trivy image sentrascan/platform:latest
```

### Regular Updates

```bash
# Update dependencies
pip list --outdated
pip install --upgrade package-name

# Update base images
docker pull python:3.11-slim
docker-compose build --no-cache
```

---

## Security Headers

```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

---

## Incident Response

### Security Incident Procedure

1. **Identify** - Detect security incident
2. **Contain** - Isolate affected systems
3. **Eradicate** - Remove threat
4. **Recover** - Restore services
5. **Lessons Learned** - Document and improve

### Incident Response Script

```bash
#!/bin/bash
# incident-response.sh

# 1. Revoke all API keys
docker-compose exec db psql -U sentrascan -d sentrascan \
  -c "UPDATE api_keys SET is_revoked = true;"

# 2. Change secrets
openssl rand -base64 64 > .env.secret
docker-compose up -d api

# 3. Review logs
docker-compose logs --tail=1000 api | grep -i "error\|unauthorized\|failed"

# 4. Notify security team
# Send alert with incident details
```

---

## Security Testing

### Penetration Testing

```bash
# Use OWASP ZAP
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://sentrascan.example.com

# Use Burp Suite
# Manual testing with Burp Suite Professional
```

### Security Audit

```bash
# Code security audit
bandit -r src/

# Dependency audit
pip-audit

# Container audit
trivy image sentrascan/platform:latest
```

---

## Next Steps

**Operations:**
- [Administrator Guide](ADMIN-GUIDE.md) - Production deployment with security hardening
- [Runbooks](RUNBOOKS.md) - Operational procedures including incident response
- [Monitoring Guide](MONITORING.md) - Security monitoring and alerting

**Reference:**
- [Technical Documentation](TECHNICAL-DOCUMENTATION.md#security-considerations) - Security considerations
- [Documentation Index](README.md) - Complete documentation overview

---

**Security Contact:** [Your security team contact]

