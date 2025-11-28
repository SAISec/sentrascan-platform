"""
Script to set up performance testing environment with production-like data.

This script creates:
- Multiple tenants (100+)
- Multiple users per tenant (1000+)
- Multiple scans per tenant (10,000+)
- Multiple findings per scan (10+)
- Realistic test data that mimics production workloads
"""

import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sentrascan.core.storage import SessionLocal, init_db
from sentrascan.core.models import Tenant, User, Scan, Finding, APIKey
from sentrascan.core.auth import create_user
from sentrascan.server import generate_api_key

# Configuration
TENANT_COUNT = 100
USERS_PER_TENANT = 100
SCANS_PER_TENANT = 1000
FINDINGS_PER_SCAN = 10

# Severity distribution (realistic)
SEVERITIES = ["critical", "high", "medium", "low"]
SEVERITY_WEIGHTS = [0.1, 0.2, 0.4, 0.3]  # More medium/low findings

# Categories (realistic)
CATEGORIES = [
    "authentication", "authorization", "cryptography", "data-protection",
    "input-validation", "output-encoding", "session-management", "error-handling",
    "logging", "configuration", "dependencies", "network"
]

# Scanners
SCANNERS = ["mcp", "model"]


def weighted_choice(choices, weights):
    """Choose an item based on weights"""
    import random
    return random.choices(choices, weights=weights)[0]


def create_performance_data():
    """Create performance testing data"""
    db = SessionLocal()
    
    try:
        print("Creating performance testing data...")
        print(f"- Tenants: {TENANT_COUNT}")
        print(f"- Users per tenant: {USERS_PER_TENANT}")
        print(f"- Scans per tenant: {SCANS_PER_TENANT}")
        print(f"- Findings per scan: {FINDINGS_PER_SCAN}")
        print()
        
        # Create tenants
        print("Creating tenants...")
        tenants = []
        for i in range(TENANT_COUNT):
            tenant = Tenant(
                id=f"perf-tenant-{i}",
                name=f"Performance Test Tenant {i}",
                is_active=True
            )
            tenants.append(tenant)
        
        db.add_all(tenants)
        db.commit()
        print(f"✓ Created {len(tenants)} tenants")
        
        # Create users
        print("Creating users...")
        total_users = 0
        for tenant in tenants:
            users = []
            for j in range(USERS_PER_TENANT):
                try:
                    user = create_user(
                        db,
                        email=f"perf-user-{tenant.id}-{j}@example.com",
                        password="TestPassword123!",
                        name=f"Performance User {j}",
                        tenant_id=tenant.id,
                        role="viewer" if j % 10 == 0 else "viewer"
                    )
                    users.append(user)
                    total_users += 1
                except Exception as e:
                    # Skip if user creation fails (e.g., duplicate)
                    pass
            
            if users:
                db.commit()
        
        print(f"✓ Created {total_users} users")
        
        # Create scans and findings
        print("Creating scans and findings...")
        total_scans = 0
        total_findings = 0
        
        for tenant_idx, tenant in enumerate(tenants):
            if tenant_idx % 10 == 0:
                print(f"  Processing tenant {tenant_idx + 1}/{len(tenants)}...")
            
            # Create scans in batches
            batch_size = 100
            for batch_start in range(0, SCANS_PER_TENANT, batch_size):
                batch_end = min(batch_start + batch_size, SCANS_PER_TENANT)
                scans = []
                
                for scan_idx in range(batch_start, batch_end):
                    scan = Scan(
                        id=f"perf-scan-{tenant.id}-{scan_idx}",
                        scan_type=SCANNERS[scan_idx % len(SCANNERS)],
                        target_path=f"/test/path/{scan_idx}",
                        passed=scan_idx % 5 != 0,  # 80% pass rate
                        tenant_id=tenant.id,
                        created_at=datetime.utcnow() - timedelta(days=scan_idx % 30)
                    )
                    scans.append(scan)
                
                db.add_all(scans)
                db.commit()
                total_scans += len(scans)
                
                # Create findings for each scan
                findings = []
                for scan in scans:
                    for finding_idx in range(FINDINGS_PER_SCAN):
                        finding = Finding(
                            id=f"perf-finding-{scan.id}-{finding_idx}",
                            scan_id=scan.id,
                            module=f"module_{finding_idx % 10}",
                            scanner=scan.scan_type,
                            severity=weighted_choice(SEVERITIES, SEVERITY_WEIGHTS),
                            category=CATEGORIES[finding_idx % len(CATEGORIES)],
                            title=f"Finding {finding_idx} in {scan.id}",
                            description=f"Description for finding {finding_idx}",
                            location=f"file_{finding_idx}.py:line_{finding_idx * 10}",
                            remediation=f"Fix finding {finding_idx}",
                            tenant_id=tenant.id
                        )
                        findings.append(finding)
                
                # Batch insert findings
                finding_batch_size = 500
                for i in range(0, len(findings), finding_batch_size):
                    db.add_all(findings[i:i+finding_batch_size])
                    db.commit()
                    total_findings += len(findings[i:i+finding_batch_size])
        
        print(f"✓ Created {total_scans} scans")
        print(f"✓ Created {total_findings} findings")
        
        # Create API keys
        print("Creating API keys...")
        api_keys = []
        for tenant in tenants[:10]:  # Create keys for first 10 tenants
            for j in range(5):  # 5 keys per tenant
                api_key = generate_api_key()
                key_hash = APIKey.hash_key(api_key)
                
                api_key_obj = APIKey(
                    id=f"perf-key-{tenant.id}-{j}",
                    name=f"Performance Key {j}",
                    key_hash=key_hash,
                    tenant_id=tenant.id,
                    role="viewer",
                    is_revoked=False
                )
                api_keys.append(api_key_obj)
        
        db.add_all(api_keys)
        db.commit()
        print(f"✓ Created {len(api_keys)} API keys")
        
        print()
        print("Performance testing data created successfully!")
        print(f"Summary:")
        print(f"  - Tenants: {TENANT_COUNT}")
        print(f"  - Users: {total_users}")
        print(f"  - Scans: {total_scans}")
        print(f"  - Findings: {total_findings}")
        print(f"  - API Keys: {len(api_keys)}")
        
    except Exception as e:
        print(f"Error creating performance data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def cleanup_performance_data():
    """Clean up performance testing data"""
    db = SessionLocal()
    
    try:
        print("Cleaning up performance testing data...")
        
        # Delete in reverse order (findings -> scans -> users -> tenants)
        db.query(Finding).filter(Finding.id.like("perf-finding-%")).delete(synchronize_session=False)
        db.query(Scan).filter(Scan.id.like("perf-scan-%")).delete(synchronize_session=False)
        db.query(User).filter(User.email.like("perf-user-%@example.com")).delete(synchronize_session=False)
        db.query(APIKey).filter(APIKey.id.like("perf-key-%")).delete(synchronize_session=False)
        db.query(Tenant).filter(Tenant.id.like("perf-tenant-%")).delete(synchronize_session=False)
        
        db.commit()
        print("✓ Performance testing data cleaned up")
        
    except Exception as e:
        print(f"Error cleaning up performance data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up performance testing data")
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up existing performance testing data"
    )
    parser.add_argument(
        "--tenants",
        type=int,
        default=TENANT_COUNT,
        help=f"Number of tenants to create (default: {TENANT_COUNT})"
    )
    parser.add_argument(
        "--users-per-tenant",
        type=int,
        default=USERS_PER_TENANT,
        help=f"Number of users per tenant (default: {USERS_PER_TENANT})"
    )
    parser.add_argument(
        "--scans-per-tenant",
        type=int,
        default=SCANS_PER_TENANT,
        help=f"Number of scans per tenant (default: {SCANS_PER_TENANT})"
    )
    parser.add_argument(
        "--findings-per-scan",
        type=int,
        default=FINDINGS_PER_SCAN,
        help=f"Number of findings per scan (default: {FINDINGS_PER_SCAN})"
    )
    
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup_performance_data()
    else:
        # Update global config
        TENANT_COUNT = args.tenants
        USERS_PER_TENANT = args.users_per_tenant
        SCANS_PER_TENANT = args.scans_per_tenant
        FINDINGS_PER_SCAN = args.findings_per_scan
        
        create_performance_data()

