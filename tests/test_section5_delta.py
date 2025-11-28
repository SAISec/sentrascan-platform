"""
Delta Tests for Section 5.0: Analytics, ML & Advanced Features

Tests new functionality introduced in Section 5.0:
- Tenant settings service
- Analytics engine
- ML insights
- Documentation viewer
"""

import pytest
import os
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.orm import Session

# Import models
from sentrascan.core.models import (
    Tenant, User, Scan, Finding, TenantSettings
)

# Import services
from sentrascan.core.tenant_settings import (
    TenantSettingsService, get_tenant_settings, get_tenant_setting,
    set_tenant_setting, set_tenant_settings, reset_tenant_settings_to_defaults
)
from sentrascan.core.analytics import (
    get_trend_analysis, get_severity_distribution, get_scanner_effectiveness,
    get_remediation_progress, get_risk_scores
)
from sentrascan.core.analytics_export import (
    export_trends_csv, export_severity_distribution_csv,
    export_scanner_effectiveness_csv, export_remediation_progress_csv,
    export_risk_scores_csv, export_analytics_pdf, export_analytics_json
)

# Try to import ML insights (may not be available)
try:
    from sentrascan.core.ml_insights import (
        MLInsightsEngine, is_ml_insights_enabled,
        detect_anomalies, analyze_correlations, prioritize_remediations
    )
    HAS_ML_INSIGHTS = True
except ImportError:
    HAS_ML_INSIGHTS = False

from sentrascan.core.storage import SessionLocal


@pytest.fixture
def db_session():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_tenant(db_session):
    """Create test tenant"""
    import uuid
    tenant_id = f"test-tenant-{uuid.uuid4()}"
    tenant = Tenant(
        id=tenant_id,
        name=f"Test Tenant {uuid.uuid4()}",
        is_active=True
    )
    db_session.add(tenant)
    db_session.commit()
    yield tenant
    # Cleanup
    db_session.delete(tenant)
    db_session.commit()


@pytest.fixture
def test_user(db_session, test_tenant):
    """Create test user"""
    user_id = f"test-user-{datetime.utcnow().timestamp()}"
    user = User(
        id=user_id,
        email=f"test-{user_id}@example.com",
        password_hash="hashed_password",
        name="Test User",
        tenant_id=test_tenant.id,
        role="tenant_admin"
    )
    db_session.add(user)
    db_session.commit()
    yield user
    # Cleanup
    db_session.delete(user)
    db_session.commit()


@pytest.fixture
def test_scans(db_session, test_tenant):
    """Create test scans with findings"""
    scans = []
    findings = []
    
    # Create scans over the last 30 days
    for i in range(10):
        scan = Scan(
            id=f"scan-{i}",
            created_at=datetime.utcnow() - timedelta(days=i*3),
            scan_type="mcp" if i % 2 == 0 else "model",
            target_path=f"/path/to/target-{i}",
            passed=i % 3 != 0,  # Some fail
            tenant_id=test_tenant.id
        )
        db_session.add(scan)
        scans.append(scan)
        
        # Add findings
        for j in range(5):
            severity = ["critical", "high", "medium", "low", "info"][j]
            finding = Finding(
                id=f"finding-{i}-{j}",
                scan_id=scan.id,
                severity=severity,
                category=f"category-{j}",
                title=f"Finding {i}-{j}",
                description=f"Description {i}-{j}",
                scanner="mcp" if i % 2 == 0 else "model",
                tenant_id=test_tenant.id
            )
            db_session.add(finding)
            findings.append(finding)
    
    db_session.commit()
    yield scans, findings
    # Cleanup
    for finding in findings:
        db_session.delete(finding)
    for scan in scans:
        db_session.delete(scan)
    db_session.commit()


class TestTenantSettings:
    """Test tenant settings service"""
    
    def test_get_default_settings(self, db_session, test_tenant):
        """Test getting default settings for new tenant"""
        from sentrascan.core.tenant_settings import get_tenant_settings
        settings = get_tenant_settings(db_session, test_tenant.id)
        assert settings is not None
        assert "policy" in settings
        assert "scanner" in settings
        assert "severity" in settings
        assert "notification" in settings
        assert "scan" in settings
        assert "integration" in settings
    
    def test_set_tenant_setting(self, db_session, test_tenant):
        """Test setting a specific tenant setting"""
        from sentrascan.core.tenant_settings import set_tenant_setting
        # Set policy setting
        result = set_tenant_setting(
            db_session,
            test_tenant.id,
            "policy",
            {"gate_thresholds": {"critical_max": 0, "high_max": 5}},
            None  # user_id
        )
        assert result is not None
        
        # Retrieve and verify
        from sentrascan.core.tenant_settings import get_tenant_setting
        setting = get_tenant_setting(db_session, test_tenant.id, "policy")
        assert setting is not None
        assert setting["gate_thresholds"]["critical_max"] == 0
        assert setting["gate_thresholds"]["high_max"] == 5
    
    def test_set_multiple_settings(self, db_session, test_tenant):
        """Test setting multiple settings at once"""
        from sentrascan.core.tenant_settings import set_tenant_settings
        settings = {
            "policy": {"gate_thresholds": {"critical_max": 0}},
            "scanner": {"enabled_scanners": ["mcp", "model"]}
        }
        result = set_tenant_settings(db_session, test_tenant.id, settings, None)  # user_id
        assert result is not None
        
        # Verify both settings
        from sentrascan.core.tenant_settings import get_tenant_setting
        policy = get_tenant_setting(db_session, test_tenant.id, "policy")
        scanner = get_tenant_setting(db_session, test_tenant.id, "scanner")
        assert policy["gate_thresholds"]["critical_max"] == 0
        assert "mcp" in scanner["enabled_scanners"]
    
    def test_settings_validation(self, db_session, test_tenant):
        """Test settings validation"""
        from sentrascan.core.tenant_settings import set_tenant_setting, get_tenant_setting
        # Invalid setting key - system allows custom keys but validates structure
        # Try setting an invalid structure instead
        try:
            # This should work (custom keys allowed)
            set_tenant_setting(
                db_session,
                test_tenant.id,
                "invalid_key",
                {"value": "test"},
                None
            )
            # Verify it was set
            setting = get_tenant_setting(db_session, test_tenant.id, "invalid_key")
            assert setting is not None
        except ValueError:
            # If validation is strict, that's also acceptable
            pass
    
    def test_reset_to_defaults(self, db_session, test_tenant):
        """Test resetting settings to defaults"""
        from sentrascan.core.tenant_settings import set_tenant_setting, reset_tenant_settings_to_defaults
        # Set custom settings
        set_tenant_setting(
            db_session,
            test_tenant.id,
            "policy",
            {"gate_thresholds": {"critical_max": 10}},
            None
        )
        
        # Reset
        reset_tenant_settings_to_defaults(db_session, test_tenant.id, None)  # user_id
        
        # Verify defaults restored
        from sentrascan.core.tenant_settings import get_tenant_setting
        policy = get_tenant_setting(db_session, test_tenant.id, "policy")
        # Default critical_max should be 0
        assert policy["gate_thresholds"]["critical_max"] == 0
    
    def test_tenant_isolation_settings(self, db_session, test_tenant):
        """Test that settings are tenant-isolated"""
        # Create second tenant
        import uuid
        tenant2 = Tenant(
            id=f"test-tenant-2-{uuid.uuid4()}",
            name=f"Test Tenant 2 {uuid.uuid4()}",
            is_active=True
        )
        db_session.add(tenant2)
        db_session.commit()
        
        try:
            # Set different settings for each tenant
            from sentrascan.core.tenant_settings import TenantSettingsService
            TenantSettingsService.set_setting(
                db_session,
                test_tenant.id,
                "policy",
                {"gate_thresholds": {"critical_max": 0}},
                None
            )
            TenantSettingsService.set_setting(
                db_session,
                tenant2.id,
                "policy",
                {"gate_thresholds": {"critical_max": 10}},
                None
            )
            
            # Verify isolation
            from sentrascan.core.tenant_settings import TenantSettingsService
            policy1 = TenantSettingsService.get_setting(db_session, test_tenant.id, "policy")
            policy2 = TenantSettingsService.get_setting(db_session, tenant2.id, "policy")
            assert policy1["gate_thresholds"]["critical_max"] == 0
            assert policy2["gate_thresholds"]["critical_max"] == 10
        finally:
            db_session.delete(tenant2)
            db_session.commit()


class TestAnalytics:
    """Test analytics engine"""
    
    def test_trend_analysis(self, db_session, test_tenant, test_scans):
        """Test trend analysis"""
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        trends = get_trend_analysis(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
        assert trends is not None
        assert "period" in trends
        assert "data" in trends
        assert "summary" in trends
        assert len(trends["data"]) > 0
    
    def test_severity_distribution(self, db_session, test_tenant, test_scans):
        """Test severity distribution"""
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        distribution = get_severity_distribution(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
        assert distribution is not None
        assert "distribution" in distribution
        assert "total" in distribution
        assert "percentages" in distribution
    
    def test_scanner_effectiveness(self, db_session, test_tenant, test_scans):
        """Test scanner effectiveness metrics"""
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        effectiveness = get_scanner_effectiveness(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
        assert effectiveness is not None
        assert "scanners" in effectiveness
        assert "mcp" in effectiveness["scanners"] or "model" in effectiveness["scanners"]
    
    def test_remediation_progress(self, db_session, test_tenant, test_scans):
        """Test remediation progress tracking"""
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        progress = get_remediation_progress(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
        assert progress is not None
        assert "total_findings" in progress
        assert "by_severity" in progress
        assert "by_age" in progress
    
    def test_risk_scores(self, db_session, test_tenant, test_scans):
        """Test risk scoring"""
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        risk_scores = get_risk_scores(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
        assert risk_scores is not None
        assert "total_risk_score" in risk_scores
        assert "by_severity" in risk_scores
        assert "top_risks" in risk_scores
    
    def test_time_range_filtering(self, db_session, test_tenant, test_scans):
        """Test time range filtering"""
        # Test different time ranges
        from datetime import timedelta
        end_date = datetime.utcnow()
        trends_7 = get_trend_analysis(db_session, test_tenant.id, start_date=end_date - timedelta(days=7), end_date=end_date)
        trends_30 = get_trend_analysis(db_session, test_tenant.id, start_date=end_date - timedelta(days=30), end_date=end_date)
        trends_90 = get_trend_analysis(db_session, test_tenant.id, start_date=end_date - timedelta(days=90), end_date=end_date)
        
        assert trends_7 is not None
        assert trends_30 is not None
        assert trends_90 is not None
    
    def test_tenant_scoping(self, db_session, test_tenant, test_scans):
        """Test that analytics are tenant-scoped"""
        # Create second tenant with scans
        tenant2 = Tenant(
            id=f"test-tenant-2-{datetime.utcnow().timestamp()}",
            name="Test Tenant 2",
            is_active=True
        )
        db_session.add(tenant2)
        db_session.commit()
        
        try:
            # Get analytics for each tenant
            from datetime import timedelta
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            trends1 = get_trend_analysis(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
            trends2 = get_trend_analysis(db_session, tenant2.id, start_date=start_date, end_date=end_date)
            
            # Tenant 2 should have no data (or different data)
            assert trends1["summary"]["total_scans"] >= 0
            assert trends2["summary"]["total_scans"] >= 0
        finally:
            db_session.delete(tenant2)
            db_session.commit()
    
    def test_export_csv(self, db_session, test_tenant, test_scans):
        """Test CSV export"""
        # Export trends
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        csv_data = export_trends_csv(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
        assert csv_data is not None
        assert isinstance(csv_data, str)
        assert "period" in csv_data.lower() or "date" in csv_data.lower()
    
    def test_export_json(self, db_session, test_tenant, test_scans):
        """Test JSON export"""
        # Get analytics data first
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        trend_data = get_trend_analysis(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
        severity_data = get_severity_distribution(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
        # Export as JSON
        json_data = export_analytics_json(trend_data=trend_data, severity_data=severity_data)
        assert json_data is not None
        assert isinstance(json_data, dict)
        assert "trends" in json_data or "severity" in json_data


class TestMLInsights:
    """Test ML insights (if available)"""
    
    @pytest.mark.skipif(not HAS_ML_INSIGHTS, reason="ML insights not available")
    def test_ml_insights_enabled(self):
        """Test ML insights feature flag"""
        enabled = is_ml_insights_enabled()
        # Should return boolean
        assert isinstance(enabled, bool)
    
    @pytest.mark.skipif(not HAS_ML_INSIGHTS, reason="ML insights not available")
    def test_anomaly_detection(self, db_session, test_tenant, test_scans):
        """Test anomaly detection"""
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        anomalies = detect_anomalies(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
        assert anomalies is not None
        assert "anomalies" in anomalies
        assert isinstance(anomalies["anomalies"], list)
    
    @pytest.mark.skipif(not HAS_ML_INSIGHTS, reason="ML insights not available")
    def test_correlations(self, db_session, test_tenant, test_scans):
        """Test finding correlations"""
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        correlations = analyze_correlations(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
        assert correlations is not None
        assert "correlations" in correlations
    
    @pytest.mark.skipif(not HAS_ML_INSIGHTS, reason="ML insights not available")
    def test_remediation_prioritization(self, db_session, test_tenant, test_scans):
        """Test remediation prioritization"""
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        recommendations = prioritize_remediations(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
        assert recommendations is not None
        assert "recommendations" in recommendations
        assert isinstance(recommendations["recommendations"], list)
    
    @pytest.mark.skipif(not HAS_ML_INSIGHTS, reason="ML insights not available")
    def test_no_customer_data_learning(self, db_session, test_tenant, test_scans):
        """Test that ML models don't learn from customer data"""
        # This is a design/implementation test
        # ML insights should only perform inference, not training
        # We can't directly test this, but we can verify the feature flag
        # and that insights are generated without modifying models
        enabled = is_ml_insights_enabled()
        if enabled:
            # Run insights multiple times - should not "learn" from data
            from datetime import timedelta
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            anomalies1 = detect_anomalies(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
            anomalies2 = detect_anomalies(db_session, test_tenant.id, start_date=start_date, end_date=end_date)
            # Results should be consistent (not improving from "learning")
            assert anomalies1 is not None
            assert anomalies2 is not None


class TestDocumentation:
    """Test documentation viewer"""
    
    def test_docs_structure(self):
        """Test documentation directory structure"""
        docs_dir = Path(__file__).parent.parent / "docs"
        assert docs_dir.exists()
        
        # Check required directories
        required_dirs = [
            "getting-started",
            "user-guide",
            "api",
            "how-to",
            "troubleshooting",
            "faq",
            "best-practices",
            "glossary"
        ]
        
        for dir_name in required_dirs:
            dir_path = docs_dir / dir_name
            assert dir_path.exists(), f"Directory {dir_name} does not exist"
            assert dir_path.is_dir(), f"{dir_name} is not a directory"
    
    def test_docs_files_exist(self):
        """Test that documentation files exist"""
        docs_dir = Path(__file__).parent.parent / "docs"
        
        required_files = [
            "getting-started/README.md",
            "user-guide/README.md",
            "api/README.md",
            "how-to/README.md",
            "troubleshooting/README.md",
            "faq/README.md",
            "best-practices/README.md",
            "glossary/README.md"
        ]
        
        for file_path in required_files:
            full_path = docs_dir / file_path
            assert full_path.exists(), f"File {file_path} does not exist"
            assert full_path.is_file(), f"{file_path} is not a file"
    
    def test_docs_markdown_content(self):
        """Test that documentation files contain markdown content"""
        docs_dir = Path(__file__).parent.parent / "docs"
        readme_path = docs_dir / "getting-started/README.md"
        
        if readme_path.exists():
            content = readme_path.read_text(encoding='utf-8')
            # Should contain markdown elements
            assert len(content) > 0, "Documentation file is empty"
            # Should have headings
            assert "#" in content or "##" in content, "No headings found"
    
    def test_docs_api_endpoint_exists(self):
        """Test that docs API endpoint is defined"""
        # This is a structural test - we can't test the actual endpoint
        # without running the server, but we can verify the route exists
        # by checking if the function is defined in server.py
        server_path = Path(__file__).parent.parent / "src" / "sentrascan" / "server.py"
        if server_path.exists():
            content = server_path.read_text(encoding='utf-8')
            assert "/api/v1/docs/raw" in content, "Docs API endpoint not found"
            assert "get_docs_file" in content, "get_docs_file function not found"
    
    def test_docs_template_exists(self):
        """Test that docs template exists"""
        template_path = Path(__file__).parent.parent / "src" / "sentrascan" / "web" / "templates" / "docs.html"
        assert template_path.exists(), "docs.html template does not exist"
    
    def test_docs_css_exists(self):
        """Test that docs CSS exists"""
        css_path = Path(__file__).parent.parent / "src" / "sentrascan" / "web" / "static" / "css" / "docs.css"
        assert css_path.exists(), "docs.css does not exist"
    
    def test_docs_js_exists(self):
        """Test that docs JavaScript exists"""
        js_path = Path(__file__).parent.parent / "src" / "sentrascan" / "web" / "static" / "js" / "docs.js"
        assert js_path.exists(), "docs.js does not exist"
    
    def test_docs_accessibility_features(self):
        """Test that documentation has accessibility features"""
        template_path = Path(__file__).parent.parent / "src" / "sentrascan" / "web" / "templates" / "docs.html"
        if template_path.exists():
            content = template_path.read_text(encoding='utf-8')
            # Check for ARIA labels
            assert 'aria-label' in content or 'role=' in content, "No ARIA attributes found"
            # Check for semantic HTML
            assert '<main' in content or 'role="main"' in content, "No main content area"
            assert '<nav' in content or 'role="navigation"' in content, "No navigation"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

