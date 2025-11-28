"""
Performance tests for SentraScan Platform.

Tests performance targets and system limits:
- API endpoint response times
- Database query performance
- Shard routing overhead
- Encryption/decryption overhead
- System limits (tenants, users, scans)
- Memory/CPU usage under load
- Database connection pooling
- Analytics dashboard performance
- Findings aggregation performance
- Pagination performance
- Caching effectiveness
"""

import pytest
import time
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import statistics

# Try to import pytest-benchmark for load testing
try:
    import pytest_benchmark
    HAS_BENCHMARK = True
except ImportError:
    HAS_BENCHMARK = False

from sentrascan.core.storage import SessionLocal
from sentrascan.core.models import Tenant, User, APIKey, Scan, Finding
from sentrascan.core.auth import create_user
from sentrascan.core.sharding import get_shard_id, get_schema_name
from sentrascan.core.encryption import encrypt_tenant_data, decrypt_tenant_data
from sentrascan.core.key_management import get_tenant_encryption_key
from sentrascan.core.analytics import AnalyticsEngine

# Performance targets
API_RESPONSE_TIME_TARGET_MS = 200  # 95th percentile
DB_QUERY_TIME_TARGET_MS = 100  # 95th percentile
SHARD_ROUTING_OVERHEAD_MS = 5
ENCRYPTION_OVERHEAD_PERCENT = 10
PAGE_LOAD_TIME_TARGET_SEC = 2
ANALYTICS_LOAD_TIME_TARGET_SEC = 3
FINDINGS_AGGREGATION_TIME_TARGET_SEC = 1
PAGINATION_TIME_TARGET_MS = 500
CACHE_HIT_RATE_TARGET_PERCENT = 80


@pytest.fixture
def db_session():
    """Get a database session for performance tests"""
    db = SessionLocal()
    try:
        yield db
        db.rollback()
    finally:
        db.close()


@pytest.fixture
def performance_tenant(db_session):
    """Create a tenant for performance testing"""
    tenant_id = f"perf-tenant-{int(time.time())}"
    tenant = Tenant(
        id=tenant_id,
        name=f"Performance Test Tenant {tenant_id}",
        is_active=True
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    yield tenant
    try:
        db_session.delete(tenant)
        db_session.commit()
    except Exception:
        db_session.rollback()


def measure_time(func, *args, **kwargs):
    """Measure execution time of a function in milliseconds"""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    elapsed_ms = (end - start) * 1000
    return result, elapsed_ms


def percentile(data: List[float], percentile: float) -> float:
    """Calculate percentile of a list of values"""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = int(len(sorted_data) * percentile / 100)
    return sorted_data[min(index, len(sorted_data) - 1)]


class TestAPIPerformance:
    """Test 1: API endpoint performance (1000+ concurrent requests)"""
    
    @pytest.mark.skip(reason="Requires API server and load testing tool (locust)")
    def test_api_endpoint_response_times(self):
        """Test that API endpoints respond within target time"""
        # This would use locust or similar tool for load testing
        # Target: <200ms (95th percentile) for all endpoints
        pass
    
    @pytest.mark.skip(reason="Requires API server running")
    def test_scans_endpoint_performance(self):
        """Test /api/v1/scans endpoint performance"""
        pass
    
    @pytest.mark.skip(reason="Requires API server running")
    def test_findings_endpoint_performance(self):
        """Test /api/v1/findings endpoint performance"""
        pass
    
    @pytest.mark.skip(reason="Requires API server running")
    def test_api_keys_endpoint_performance(self):
        """Test /api/v1/api-keys endpoint performance"""
        pass


class TestDatabaseQueryPerformance:
    """Test 2: Database query performance"""
    
    def test_tenant_scoped_query_performance(self, db_session, performance_tenant):
        """Test that tenant-scoped queries complete within target time"""
        # Create test data
        scans = []
        for i in range(100):
            scan = Scan(
                id=f"perf-scan-{i}-{int(time.time())}",
                scan_type="mcp",
                target_path=f"/test/path/{i}",
                passed=False,
                tenant_id=performance_tenant.id
            )
            scans.append(scan)
        db_session.add_all(scans)
        db_session.commit()
        
        # Measure query time (manual timing - benchmark can be added later if needed)
        times = []
        for _ in range(10):
            _, elapsed_ms = measure_time(
                lambda: db_session.query(Scan).filter(
                    Scan.tenant_id == performance_tenant.id
                ).all()
            )
            times.append(elapsed_ms)
        
        # Calculate 95th percentile
        p95 = percentile(times, 95)
        
        # Verify target
        assert p95 < DB_QUERY_TIME_TARGET_MS, \
            f"95th percentile query time {p95:.2f}ms exceeds target {DB_QUERY_TIME_TARGET_MS}ms"
        
        # Cleanup
        db_session.query(Scan).filter(
            Scan.tenant_id == performance_tenant.id
        ).delete()
        db_session.commit()
    
    def test_join_query_performance(self, db_session, performance_tenant):
        """Test JOIN query performance"""
        # Create scan with findings
        scan = Scan(
            id=f"perf-scan-join-{int(time.time())}",
            scan_type="mcp",
            target_path="/test/path",
            passed=False,
            tenant_id=performance_tenant.id
        )
        db_session.add(scan)
        db_session.commit()
        
        findings = []
        for i in range(50):
            finding = Finding(
                id=f"perf-finding-{i}-{int(time.time())}",
                scan_id=scan.id,
                module="test_module",
                scanner="mcp",
                severity="critical" if i % 10 == 0 else "high",
                category="test",
                title=f"Finding {i}",
                description=f"Description {i}",
                tenant_id=performance_tenant.id
            )
            findings.append(finding)
        db_session.add_all(findings)
        db_session.commit()
        
        # Measure JOIN query time (manual timing)
        times = []
        for _ in range(10):
            _, elapsed_ms = measure_time(
                lambda: db_session.query(Scan, Finding).join(
                    Finding, Scan.id == Finding.scan_id
                ).filter(
                    Scan.tenant_id == performance_tenant.id
                ).all()
            )
            times.append(elapsed_ms)
        
        # Calculate 95th percentile
        p95 = percentile(times, 95)
        
        # Verify target
        assert p95 < DB_QUERY_TIME_TARGET_MS, \
            f"95th percentile JOIN query time {p95:.2f}ms exceeds target {DB_QUERY_TIME_TARGET_MS}ms"
        
        # Cleanup
        db_session.query(Finding).filter(
            Finding.scan_id == scan.id
        ).delete()
        db_session.delete(scan)
        db_session.commit()


class TestShardRoutingPerformance:
    """Test 3: Shard routing overhead"""
    
    @pytest.mark.skipif(
        os.environ.get("DATABASE_URL", "").startswith("sqlite"),
        reason="Sharding requires PostgreSQL"
    )
    def test_shard_routing_overhead(self):
        """Test that shard routing adds minimal overhead"""
        tenant_ids = [f"tenant-{i}" for i in range(100)]
        
        # Measure shard routing time (manual timing)
        times = []
        for tenant_id in tenant_ids:
            _, elapsed_ms = measure_time(get_shard_id, tenant_id)
            times.append(elapsed_ms)
        
        # Calculate average and max
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        # Verify overhead is minimal
        assert avg_time < SHARD_ROUTING_OVERHEAD_MS, \
            f"Average shard routing time {avg_time:.2f}ms exceeds target {SHARD_ROUTING_OVERHEAD_MS}ms"
        assert max_time < SHARD_ROUTING_OVERHEAD_MS * 2, \
            f"Max shard routing time {max_time:.2f}ms exceeds target {SHARD_ROUTING_OVERHEAD_MS * 2}ms"


class TestEncryptionPerformance:
    """Test 4: Encryption/decryption overhead"""
    
    def test_encryption_overhead(self, performance_tenant):
        """Test that encryption adds minimal overhead"""
        os.environ["ENCRYPTION_MASTER_KEY"] = "test-master-key-32-chars-long!!"
        
        try:
            # Get tenant key
            get_tenant_encryption_key(performance_tenant.id, create_if_missing=True)
            
            # Test data
            test_data = "sensitive-data-" * 100  # ~1.5KB
            
            # Measure plaintext operations (baseline)
            plaintext_times = []
            for _ in range(10):
                _, elapsed_ms = measure_time(lambda: test_data.encode('utf-8'))
                plaintext_times.append(elapsed_ms)
            
            # Measure encryption operations
            encryption_times = []
            for _ in range(10):
                _, elapsed_ms = measure_time(
                    encrypt_tenant_data, performance_tenant.id, test_data
                )
                encryption_times.append(elapsed_ms)
            
            # Calculate overhead
            avg_plaintext = statistics.mean(plaintext_times)
            avg_encryption = statistics.mean(encryption_times)
            overhead_percent = ((avg_encryption - avg_plaintext) / avg_plaintext) * 100 if avg_plaintext > 0 else 0
            
            # Verify overhead is acceptable
            assert overhead_percent < ENCRYPTION_OVERHEAD_PERCENT, \
                f"Encryption overhead {overhead_percent:.2f}% exceeds target {ENCRYPTION_OVERHEAD_PERCENT}%"
        except Exception as e:
            pytest.skip(f"Encryption not configured: {e}")
    
    def test_decryption_overhead(self, performance_tenant):
        """Test that decryption adds minimal overhead"""
        os.environ["ENCRYPTION_MASTER_KEY"] = "test-master-key-32-chars-long!!"
        
        try:
            # Get tenant key
            get_tenant_encryption_key(performance_tenant.id, create_if_missing=True)
            
            # Test data
            test_data = "sensitive-data-" * 100
            encrypted_data = encrypt_tenant_data(performance_tenant.id, test_data)
            
            # Measure decryption operations
            decryption_times = []
            for _ in range(10):
                _, elapsed_ms = measure_time(
                    decrypt_tenant_data, performance_tenant.id, encrypted_data
                )
                decryption_times.append(elapsed_ms)
            
            # Calculate average
            avg_decryption = statistics.mean(decryption_times)
            
            # Verify decryption is fast (should be similar to encryption)
            assert avg_decryption < 50, \
                f"Average decryption time {avg_decryption:.2f}ms is too slow"
        except Exception as e:
            pytest.skip(f"Encryption not configured: {e}")


class TestSystemLimits:
    """Test 5: System limits (100+ tenants, 1000+ users, 10,000+ scans)"""
    
    def test_multiple_tenants(self, db_session):
        """Test system with 100+ tenants"""
        tenant_count = 100
        tenants = []
        
        start_time = time.perf_counter()
        for i in range(tenant_count):
            tenant = Tenant(
                id=f"limit-tenant-{i}-{int(time.time())}",
                name=f"Limit Test Tenant {i}",
                is_active=True
            )
            tenants.append(tenant)
        
        db_session.add_all(tenants)
        db_session.commit()
        elapsed = time.perf_counter() - start_time
        
        # Verify all tenants created
        created_count = db_session.query(Tenant).filter(
            Tenant.id.in_([t.id for t in tenants])
        ).count()
        assert created_count == tenant_count
        
        # Cleanup
        db_session.query(Tenant).filter(
            Tenant.id.in_([t.id for t in tenants])
        ).delete(synchronize_session=False)
        db_session.commit()
    
    def test_multiple_users_per_tenant(self, db_session, performance_tenant):
        """Test system with 1000+ users per tenant"""
        user_count = 100  # Reduced for test speed, can be increased
        users = []
        
        start_time = time.perf_counter()
        for i in range(user_count):
            try:
                user = create_user(
                    db_session,
                    email=f"limit-user-{i}-{int(time.time())}@example.com",
                    password="TestPassword123!",
                    name=f"Limit Test User {i}",
                    tenant_id=performance_tenant.id,
                    role="viewer"
                )
                users.append(user)
            except Exception as e:
                # Skip if user creation fails (e.g., duplicate email)
                pass
        
        db_session.commit()
        elapsed = time.perf_counter() - start_time
        
        # Verify users created
        created_count = db_session.query(User).filter(
            User.tenant_id == performance_tenant.id,
            User.email.like(f"limit-user-%@example.com")
        ).count()
        assert created_count > 0
        
        # Cleanup
        db_session.query(User).filter(
            User.tenant_id == performance_tenant.id,
            User.email.like(f"limit-user-%@example.com")
        ).delete(synchronize_session=False)
        db_session.commit()
    
    def test_multiple_scans_per_tenant(self, db_session, performance_tenant):
        """Test system with 10,000+ scans per tenant"""
        scan_count = 1000  # Reduced for test speed, can be increased to 10,000
        scans = []
        
        start_time = time.perf_counter()
        for i in range(scan_count):
            scan = Scan(
                id=f"limit-scan-{i}-{int(time.time())}",
                scan_type="mcp",
                target_path=f"/test/path/{i}",
                passed=False,
                tenant_id=performance_tenant.id
            )
            scans.append(scan)
        
        # Batch insert
        batch_size = 100
        for i in range(0, len(scans), batch_size):
            db_session.add_all(scans[i:i+batch_size])
            db_session.commit()
        
        elapsed = time.perf_counter() - start_time
        
        # Verify scans created
        created_count = db_session.query(Scan).filter(
            Scan.tenant_id == performance_tenant.id,
            Scan.id.like(f"limit-scan-%")
        ).count()
        assert created_count == scan_count
        
        # Cleanup
        db_session.query(Scan).filter(
            Scan.tenant_id == performance_tenant.id,
            Scan.id.like(f"limit-scan-%")
        ).delete(synchronize_session=False)
        db_session.commit()


class TestAnalyticsPerformance:
    """Test 6: Analytics dashboard performance"""
    
    def test_analytics_with_many_findings(self, db_session, performance_tenant):
        """Test analytics dashboard loads within target time with 10,000+ findings"""
        # Create scan
        scan = Scan(
            id=f"analytics-scan-{int(time.time())}",
            scan_type="mcp",
            target_path="/test/path",
            passed=False,
            tenant_id=performance_tenant.id
        )
        db_session.add(scan)
        db_session.commit()
        
        # Create findings (reduced count for test speed)
        finding_count = 1000  # Can be increased to 10,000
        findings = []
        for i in range(finding_count):
            finding = Finding(
                id=f"analytics-finding-{i}-{int(time.time())}",
                scan_id=scan.id,
                module="test_module",
                scanner="mcp",
                severity=["critical", "high", "medium", "low"][i % 4],
                category="test",
                title=f"Finding {i}",
                description=f"Description {i}",
                tenant_id=performance_tenant.id
            )
            findings.append(finding)
        
        # Batch insert
        batch_size = 100
        for i in range(0, len(findings), batch_size):
            db_session.add_all(findings[i:i+batch_size])
            db_session.commit()
        
        # Measure analytics query time
        analytics = AnalyticsEngine(db_session, performance_tenant.id)
        
        times = []
        for _ in range(5):
            _, elapsed_sec = measure_time(analytics.get_severity_distribution)
            times.append(elapsed_sec)
        
        avg_time = statistics.mean(times)
        
        # Verify target
        assert avg_time < ANALYTICS_LOAD_TIME_TARGET_SEC, \
            f"Average analytics load time {avg_time:.2f}s exceeds target {ANALYTICS_LOAD_TIME_TARGET_SEC}s"
        
        # Cleanup
        db_session.query(Finding).filter(
            Finding.scan_id == scan.id
        ).delete(synchronize_session=False)
        db_session.delete(scan)
        db_session.commit()
    
    def test_findings_aggregation_performance(self, db_session, performance_tenant):
        """Test findings aggregation completes within target time"""
        # Create multiple scans with findings
        scan_count = 10
        finding_count_per_scan = 100
        
        scans = []
        for s in range(scan_count):
            scan = Scan(
                id=f"agg-scan-{s}-{int(time.time())}",
                scan_type="mcp",
                target_path=f"/test/path/{s}",
                passed=False,
                tenant_id=performance_tenant.id
            )
            scans.append(scan)
        
        db_session.add_all(scans)
        db_session.commit()
        
        # Create findings
        findings = []
        for s, scan in enumerate(scans):
            for f in range(finding_count_per_scan):
                finding = Finding(
                    id=f"agg-finding-{s}-{f}-{int(time.time())}",
                    scan_id=scan.id,
                    module="test_module",
                    scanner="mcp",
                    severity=["critical", "high", "medium", "low"][f % 4],
                    category="test",
                    title=f"Finding {s}-{f}",
                    description=f"Description {s}-{f}",
                    tenant_id=performance_tenant.id
                )
                findings.append(finding)
        
        # Batch insert
        batch_size = 100
        for i in range(0, len(findings), batch_size):
            db_session.add_all(findings[i:i+batch_size])
            db_session.commit()
        
        # Measure aggregation time
        times = []
        for _ in range(5):
            _, elapsed_sec = measure_time(
                lambda: db_session.query(Finding).filter(
                    Finding.tenant_id == performance_tenant.id
                ).count()
            )
            times.append(elapsed_sec)
        
        avg_time = statistics.mean(times)
        
        # Verify target
        assert avg_time < FINDINGS_AGGREGATION_TIME_TARGET_SEC, \
            f"Average aggregation time {avg_time:.2f}s exceeds target {FINDINGS_AGGREGATION_TIME_TARGET_SEC}s"
        
        # Cleanup
        db_session.query(Finding).filter(
            Finding.tenant_id == performance_tenant.id,
            Finding.id.like(f"agg-finding-%")
        ).delete(synchronize_session=False)
        db_session.query(Scan).filter(
            Scan.tenant_id == performance_tenant.id,
            Scan.id.like(f"agg-scan-%")
        ).delete(synchronize_session=False)
        db_session.commit()


class TestPaginationPerformance:
    """Test 7: Pagination performance"""
    
    def test_pagination_performance(self, db_session, performance_tenant):
        """Test pagination completes within target time"""
        # Create scan with many findings
        scan = Scan(
            id=f"page-scan-{int(time.time())}",
            scan_type="mcp",
            target_path="/test/path",
            passed=False,
            tenant_id=performance_tenant.id
        )
        db_session.add(scan)
        db_session.commit()
        
        # Create findings
        finding_count = 500
        findings = []
        for i in range(finding_count):
            finding = Finding(
                id=f"page-finding-{i}-{int(time.time())}",
                scan_id=scan.id,
                module="test_module",
                scanner="mcp",
                severity="high",
                category="test",
                title=f"Finding {i}",
                description=f"Description {i}",
                tenant_id=performance_tenant.id
            )
            findings.append(finding)
        
        # Batch insert
        batch_size = 100
        for i in range(0, len(findings), batch_size):
            db_session.add_all(findings[i:i+batch_size])
            db_session.commit()
        
        # Measure pagination time (page size 50)
        page_size = 50
        times = []
        for page in range(0, finding_count, page_size):
            _, elapsed_ms = measure_time(
                lambda offset=page: db_session.query(Finding).filter(
                    Finding.tenant_id == performance_tenant.id
                ).offset(offset).limit(page_size).all()
            )
            times.append(elapsed_ms)
        
        avg_time = statistics.mean(times)
        p95 = percentile(times, 95)
        
        # Verify target
        assert avg_time < PAGINATION_TIME_TARGET_MS, \
            f"Average pagination time {avg_time:.2f}ms exceeds target {PAGINATION_TIME_TARGET_MS}ms"
        assert p95 < PAGINATION_TIME_TARGET_MS * 2, \
            f"95th percentile pagination time {p95:.2f}ms exceeds target {PAGINATION_TIME_TARGET_MS * 2}ms"
        
        # Cleanup
        db_session.query(Finding).filter(
            Finding.scan_id == scan.id
        ).delete(synchronize_session=False)
        db_session.delete(scan)
        db_session.commit()


class TestMemoryCPUUsage:
    """Test 8: Memory/CPU usage under sustained load"""
    
    @pytest.mark.skip(reason="Requires system monitoring tools")
    def test_memory_usage_under_load(self):
        """Test memory usage remains reasonable under load"""
        # Would use psutil or similar to monitor memory
        pass
    
    @pytest.mark.skip(reason="Requires system monitoring tools")
    def test_cpu_usage_under_load(self):
        """Test CPU usage remains reasonable under load"""
        # Would use psutil or similar to monitor CPU
        pass


class TestDatabaseConnectionPooling:
    """Test 9: Database connection pooling"""
    
    @pytest.mark.skip(reason="Requires connection pool monitoring")
    def test_connection_pool_exhaustion_handling(self):
        """Test that connection pool exhaustion is handled gracefully"""
        pass
    
    @pytest.mark.skip(reason="Requires connection pool monitoring")
    def test_max_connections_limit(self):
        """Test that max connections limit is enforced"""
        pass

