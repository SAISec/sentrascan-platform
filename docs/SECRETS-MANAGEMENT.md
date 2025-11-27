# Secrets Management Guide

## Overview

SentraScan Platform follows security best practices for secrets management. Secrets are never stored in code, environment variables, or configuration files in plaintext.

## Secrets Storage

### Master Encryption Key

The master encryption key (`ENCRYPTION_MASTER_KEY`) must be provided via:
- **Production**: Secure secrets management service (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault)
- **Development**: Environment variable (for local development only)

**Never commit secrets to version control.**

### Session Secret

The session secret (`SENTRASCAN_SECRET`) must be provided via:
- **Production**: Secure secrets management service
- **Development**: Environment variable

### Database Credentials

Database credentials (`DATABASE_URL`) must be provided via:
- **Production**: Secure secrets management service or Docker secrets
- **Development**: Environment variable or docker-compose.yml (not committed)

## Implementation

### Local Key Management

The platform includes a local key management implementation (`core/key_management.py`) that:
- Stores tenant-specific encryption keys encrypted with the master key
- Never stores keys in the database or application code
- Uses secure file storage with restricted permissions (700 for directory, 600 for files)

### Integration with External KMS

The key management module is designed to be easily extended to integrate with:
- HashiCorp Vault
- AWS KMS
- Azure Key Vault
- Google Cloud KMS

To integrate, implement a new `KeyManager` subclass that uses the external KMS service.

## Best Practices

1. **Never store secrets in code**
2. **Use secrets management services in production**
3. **Rotate secrets regularly**
4. **Use different secrets for different environments**
5. **Audit secret access** (implemented via audit logging)
6. **Encrypt secrets at rest** (implemented for tenant keys)

## Environment Variables

Required secrets (must be provided via secrets management):
- `ENCRYPTION_MASTER_KEY` - Master encryption key (32+ bytes)
- `SENTRASCAN_SECRET` - Session signing secret
- `DATABASE_URL` - Database connection string (contains credentials)

Optional secrets:
- `ENCRYPTION_KEYS_DIR` - Directory for storing encrypted tenant keys (default: `/app/keys`)

## Docker Secrets

For Docker deployments, use Docker secrets:

```yaml
services:
  api:
    secrets:
      - encryption_master_key
      - session_secret
      - database_url

secrets:
  encryption_master_key:
    external: true
  session_secret:
    external: true
  database_url:
    external: true
```

## Key Rotation

Encryption keys can be rotated via:
- API endpoint: `POST /api/v1/tenants/{tenant_id}/rotate-key` (super admin only)
- Old keys are retained for decrypting existing data
- New data is encrypted with the new key

