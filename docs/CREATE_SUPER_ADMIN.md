# Creating a Super Admin User in Hardened Container

## Overview

The SentraScan Platform includes a CLI command to create the first super admin user and default tenant. This is essential for initial deployment and bootstrapping the system.

## Prerequisites

1. The hardened container must be running and healthy
2. The database container must be running and accessible
3. Environment variables must be properly configured (especially `DATABASE_URL`)

## Method 1: Interactive Mode (Recommended)

Run the command interactively, and you'll be prompted for each field:

```bash
docker compose -f docker-compose.protected.yml exec api \
  /usr/bin/python3 -m sentrascan.cli user create-super-admin
```

You'll be prompted for:
- **Email address**: The email for the super admin account
- **Password**: The password (input will be hidden, with confirmation prompt)
- **Full name**: The display name for the user
- **Tenant name**: (Optional, defaults to "Default Tenant") - Only used if no tenants exist

### Example Interactive Session

```bash
$ docker compose -f docker-compose.protected.yml exec api \
    /usr/bin/python3 -m sentrascan.cli user create-super-admin

Email address: admin@example.com
Password: ********
Repeat for confirmation: ********
Full name: System Administrator
Tenant name [Default Tenant]: My Organization

Creating default tenant: My Organization
✓ Tenant created with ID: abc123-def456-...
Creating super admin user: admin@example.com
✓ Super admin user created successfully!
  Email: admin@example.com
  Name: System Administrator
  Role: super_admin
  Tenant: My Organization
  User ID: xyz789-uvw012-...

You can now log in at http://localhost:8200/login
```

## Method 2: Non-Interactive Mode (All Arguments Provided)

Provide all arguments directly to avoid prompts:

```bash
docker compose -f docker-compose.protected.yml exec api \
  /usr/bin/python3 -m sentrascan.cli user create-super-admin \
    --email admin@example.com \
    --password "SecurePassword123!" \
    --name "System Administrator" \
    --tenant-name "My Organization"
```

### Example Non-Interactive Command

```bash
docker compose -f docker-compose.protected.yml exec api \
  /usr/bin/python3 -m sentrascan.cli user create-super-admin \
    --email admin@example.com \
    --password "MySecurePass123!" \
    --name "Admin User" \
    --tenant-name "Default Tenant"
```

## Behavior

### First Deployment (No Tenants Exist)

If no tenants exist in the database:
1. Creates a new tenant with the provided name (or "Default Tenant" if not specified)
2. Creates the super admin user associated with that tenant
3. Sets the user's role to `super_admin`

### Existing Tenants

If tenants already exist:
1. Uses the first active tenant found in the database
2. Creates the super admin user associated with that tenant
3. Sets the user's role to `super_admin`

## Error Handling

### User Already Exists

If a user with the provided email already exists:

```
Error: User with email admin@example.com already exists.
```

**Solution:** Use a different email address or log in with the existing account.

### Database Connection Issues

If the database is not accessible:

```
Error creating super admin: (psycopg2.OperationalError) connection to server...
```

**Solution:** 
1. Verify the database container is running: `docker compose -f docker-compose.protected.yml ps`
2. Check `DATABASE_URL` environment variable is correct
3. Ensure the database is healthy and accepting connections

### No Active Tenants

If no active tenants exist and the creation fails:

```
Error: No active tenants found. Please create a tenant first.
```

**Solution:** This should not occur if the command is working correctly, as it creates a tenant automatically. If you see this, there may be a database issue.

## Security Considerations

1. **Password Strength**: The password must meet the platform's password policy:
   - Minimum 12 characters
   - At least one uppercase letter
   - At least one lowercase letter
   - At least one digit
   - At least one special character

2. **Email Uniqueness**: Each email address can only be used once in the system.

3. **First User**: The first super admin created will have full system access, including:
   - Creating and managing tenants
   - Creating and managing users
   - Access to all system features

## Verification

After creating the super admin, verify it was created successfully:

```bash
# Check container logs
docker compose -f docker-compose.protected.yml logs api | grep -i "super admin"

# Or try logging in at http://localhost:8200/login
```

## Troubleshooting

### Command Not Found

If you see `command not found` or `No module named sentrascan.cli`:

1. Verify the container is using the correct image:
   ```bash
   docker compose -f docker-compose.protected.yml ps
   ```

2. Check that the container is healthy:
   ```bash
   docker compose -f docker-compose.protected.yml ps api
   ```

3. Rebuild the container if needed:
   ```bash
   docker compose -f docker-compose.protected.yml build api
   docker compose -f docker-compose.protected.yml up -d
   ```

### Permission Denied

If you see permission errors, ensure:
- The database user has proper permissions
- The `DATABASE_URL` is correctly configured
- The database schema exists (run migrations if needed)

## Alternative: Using Standard Docker Compose

If you're using the standard (non-protected) docker-compose setup:

```bash
docker compose exec api sentrascan user create-super-admin
```

Or with the Python module:

```bash
docker compose exec api python -m sentrascan.cli user create-super-admin
```

## Next Steps

After creating the super admin:

1. **Log in** at `http://localhost:8200/login` using the email and password you provided
2. **Create additional tenants** (if needed) via the Tenant Management interface
3. **Create additional users** via the User Management interface
4. **Configure tenant settings** as needed

## Related Documentation

- [User Management Guide](USER_MANAGEMENT.md)
- [Tenant Management Guide](TENANT_MANAGEMENT.md)
- [Authentication Guide](AUTHENTICATION.md)

