import json
import os
import sys
import tempfile
import uuid
import click

from sentrascan.core.policy import PolicyEngine
from sentrascan.core.storage import init_db, SessionLocal
from sentrascan.modules.model.scanner import ModelScanner
from sentrascan.modules.mcp.scanner import MCPScanner
from sentrascan.server import run_server

@click.group()
@click.version_option()
def main():
    """SentraScan Platform CLI"""
    pass

@main.command()
@click.argument("path", nargs=-1, required=True)
@click.option("--sbom", "sbom_path", type=click.Path(dir_okay=False), help="Write CycloneDX SBOM to file")
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "markdown", "sarif"]))
@click.option("--output", "output", type=click.Path(dir_okay=False), help="Write scan report to file")
@click.option("--baseline", type=click.Path(dir_okay=False))
@click.option("--strict", is_flag=True, default=False)
@click.option("--policy", type=click.Path(dir_okay=False))
@click.option("--timeout", type=int, default=0, help="Timeout in seconds")
def model(path, sbom_path, fmt, output, baseline, strict, policy, timeout):
    pe = PolicyEngine.from_file(policy) if policy else PolicyEngine.default_model()
    ms = ModelScanner(policy=pe)
    db = SessionLocal()
    try:
        scan = ms.scan(paths=list(path), sbom_path=sbom_path, strict=strict, timeout=timeout, db=db)
        report = ms.to_report(scan)
        if output:
            with open(output, "w") as f:
                f.write(json.dumps(report, indent=2))
        else:
            click.echo(json.dumps(report, indent=2))
        sys.exit(0 if report["gate_result"]["passed"] else 1)
    finally:
        db.close()

@main.command()
@click.option("--config", "configs", multiple=True, type=click.Path(dir_okay=False), help="MCP config file(s)")
@click.option("--auto-discover", is_flag=True, default=False)
@click.option("--baseline", type=click.Path(dir_okay=False))
@click.option("--policy", type=click.Path(dir_okay=False))
@click.option("--timeout", type=int, default=60)
def mcp(configs, auto_discover, baseline, policy, timeout):
    pe = PolicyEngine.from_file(policy) if policy else PolicyEngine.default_mcp()
    scanner = MCPScanner(policy=pe)
    db = SessionLocal()
    try:
        scan = scanner.scan(config_paths=list(configs), auto_discover=auto_discover, timeout=timeout, db=db)
        report = scanner.to_report(scan)
        click.echo(json.dumps(report, indent=2))
        sys.exit(0 if report["gate_result"]["passed"] else 1)
    finally:
        db.close()

@main.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8200, type=int)
def server(host, port):
    # Check container access before starting server
    from sentrascan.core.container_protection import check_container_access
    check_container_access()
    run_server(host, port)

@main.group()
def db():
    pass

@main.group()
def auth():
    """API key management"""
    pass

@auth.command("create")
@click.option("--name", required=True)
@click.option("--role", required=True, type=click.Choice(["admin","viewer"]))
def auth_create(name, role):
    import secrets, hashlib
    from sentrascan.core.models import APIKey
    key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    db = SessionLocal()
    try:
        rec = APIKey(name=name, role=role, key_hash=key_hash)
        db.add(rec)
        db.commit()
        click.echo("API key created. Save it now; you won't be able to retrieve it later:")
        click.echo(key)
    finally:
        db.close()

@db.command("init")
def db_init():
    init_db()
    click.echo("Database initialized")


@main.command()
def doctor():
    ok, details = ModelScanner.doctor()
    click.echo(details)
    sys.exit(0 if ok else 2)

@main.group()
def user():
    """User management"""
    pass

@user.command("create-super-admin")
@click.option("--email", required=True, prompt="Email address")
@click.option("--password", required=True, prompt="Password", hide_input=True, confirmation_prompt=True)
@click.option("--name", required=True, prompt="Full name")
@click.option("--tenant-name", default="Default Tenant", help="Name for the default tenant (if creating first tenant)")
def create_super_admin(email, password, name, tenant_name):
    """
    Create the first super admin user and default tenant.
    Use this command on first deployment to bootstrap the system.
    """
    from sentrascan.core.models import Tenant, User
    from sentrascan.core.auth import create_user
    
    db = SessionLocal()
    try:
        # Check if any tenants exist
        existing_tenants = db.query(Tenant).count()
        
        if existing_tenants == 0:
            # Create default tenant
            click.echo(f"Creating default tenant: {tenant_name}")
            tenant = Tenant(
                name=tenant_name,
                is_active=True,
                settings={}
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            tenant_id = tenant.id
            click.echo(f"✓ Tenant created with ID: {tenant_id}")
        else:
            # Use first tenant or ask which one
            tenant = db.query(Tenant).filter(Tenant.is_active == True).first()
            if not tenant:
                click.echo("Error: No active tenants found. Please create a tenant first.")
                sys.exit(1)
            tenant_id = tenant.id
            click.echo(f"Using existing tenant: {tenant.name} (ID: {tenant_id})")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email.lower()).first()
        if existing_user:
            click.echo(f"Error: User with email {email} already exists.")
            sys.exit(1)
        
        # Create super admin user
        click.echo(f"Creating super admin user: {email}")
        user = create_user(
            db=db,
            email=email,
            password=password,
            name=name,
            tenant_id=tenant_id,
            role="super_admin"
        )
        
        click.echo("✓ Super admin user created successfully!")
        click.echo(f"  Email: {user.email}")
        click.echo(f"  Name: {user.name}")
        click.echo(f"  Role: {user.role}")
        click.echo(f"  Tenant: {tenant.name}")
        click.echo(f"  User ID: {user.id}")
        click.echo("\nYou can now log in at http://localhost:8200/login")
        
    except Exception as e:
        db.rollback()
        click.echo(f"Error creating super admin: {e}", err=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()