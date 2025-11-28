"""
ML Insights Module

Provides machine learning-based insights for security scan data.
IMPORTANT: ML models do NOT learn from customer data. All models use
pre-trained weights or synthetic training data only.
"""

import os
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from sentrascan.core.models import Scan, Finding
from sentrascan.core.query_helpers import filter_by_tenant
import structlog

logger = structlog.get_logger(__name__)

# Feature flag for ML insights
ML_INSIGHTS_ENABLED = os.environ.get("ML_INSIGHTS_ENABLED", "false").lower() == "true"

# Try to import scikit-learn
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from scipy.stats import pearsonr
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logger.warning("scikit-learn not available. ML insights will be disabled.")


class MLInsightsEngine:
    """
    ML Insights Engine for security scan analysis.
    
    CRITICAL: This engine does NOT train on customer data.
    All models use pre-trained weights or synthetic data only.
    """
    
    def __init__(self, db: Session, tenant_id: str):
        """
        Initialize ML insights engine.
        
        Args:
            db: Database session
            tenant_id: Tenant ID for data scoping
        """
        self.db = db
        self.tenant_id = tenant_id
        self._anomaly_model = None
        self._scaler = None
    
    def _get_synthetic_training_data(self) -> np.ndarray:
        """
        Generate synthetic training data for anomaly detection.
        This ensures we never train on customer data.
        
        Returns:
            numpy array of synthetic feature vectors
        """
        # Generate synthetic data with realistic patterns
        np.random.seed(42)  # For reproducibility
        n_samples = 1000
        
        # Features: [total_findings, critical_count, high_count, scan_duration_ms, findings_per_second]
        synthetic_data = np.random.randn(n_samples, 5)
        
        # Normalize to realistic ranges
        synthetic_data[:, 0] = np.abs(synthetic_data[:, 0] * 50 + 10)  # total_findings: 0-100
        synthetic_data[:, 1] = np.abs(synthetic_data[:, 1] * 10)  # critical_count: 0-20
        synthetic_data[:, 2] = np.abs(synthetic_data[:, 2] * 20)  # high_count: 0-40
        synthetic_data[:, 3] = np.abs(synthetic_data[:, 3] * 100000 + 50000)  # duration_ms: 0-200000
        synthetic_data[:, 4] = synthetic_data[:, 0] / (synthetic_data[:, 3] / 1000 + 1)  # findings_per_second
        
        return synthetic_data
    
    def _train_anomaly_model(self) -> None:
        """
        Train anomaly detection model using synthetic data only.
        This is called once and the model is reused.
        """
        if not HAS_SKLEARN:
            return
        
        if self._anomaly_model is not None:
            return  # Already trained
        
        try:
            # Use synthetic data for training
            synthetic_data = self._get_synthetic_training_data()
            
            # Scale features
            self._scaler = StandardScaler()
            scaled_data = self._scaler.fit_transform(synthetic_data)
            
            # Train Isolation Forest on synthetic data
            self._anomaly_model = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42,
                n_estimators=100
            )
            self._anomaly_model.fit(scaled_data)
            
            logger.info("anomaly_model_trained", source="synthetic_data", samples=len(synthetic_data))
        except Exception as e:
            logger.error("anomaly_model_training_failed", error=str(e))
            self._anomaly_model = None
    
    def detect_anomalies(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Detect anomalous scans using Isolation Forest.
        Model is trained on synthetic data only, never on customer data.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary with anomaly detection results
        """
        if not HAS_SKLEARN or not ML_INSIGHTS_ENABLED:
            return {
                "enabled": False,
                "message": "ML insights not available (scikit-learn not installed or ML_INSIGHTS_ENABLED=false)"
            }
        
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Train model on synthetic data (if not already trained)
        self._train_anomaly_model()
        
        if self._anomaly_model is None:
            return {
                "enabled": False,
                "message": "Anomaly detection model not available"
            }
        
        # Query scans
        q_scans = self.db.query(Scan).filter(
            and_(
                Scan.tenant_id == self.tenant_id,
                Scan.created_at >= start_date,
                Scan.created_at <= end_date
            )
        )
        
        scans = q_scans.all()
        
        if len(scans) < 2:
            return {
                "enabled": True,
                "anomalies": [],
                "total_scans": len(scans),
                "message": "Insufficient data for anomaly detection (need at least 2 scans)"
            }
        
        # Extract features from scans
        features = []
        scan_ids = []
        
        for scan in scans:
            # Features: [total_findings, critical_count, high_count, duration_ms, findings_per_second]
            total_findings = scan.total_findings or 0
            critical_count = scan.critical_count or 0
            high_count = scan.high_count or 0
            duration_ms = scan.duration_ms or 0
            findings_per_second = total_findings / (duration_ms / 1000 + 1) if duration_ms > 0 else 0
            
            features.append([total_findings, critical_count, high_count, duration_ms, findings_per_second])
            scan_ids.append(scan.id)
        
        # Scale features using the same scaler from training
        features_array = np.array(features)
        scaled_features = self._scaler.transform(features_array)
        
        # Predict anomalies (inference only, no training)
        predictions = self._anomaly_model.predict(scaled_features)
        anomaly_scores = self._anomaly_model.score_samples(scaled_features)
        
        # Identify anomalies (prediction == -1)
        anomalies = []
        for i, (scan_id, pred, score) in enumerate(zip(scan_ids, predictions, anomaly_scores)):
            if pred == -1:  # Anomaly detected
                scan = next(s for s in scans if s.id == scan_id)
                anomalies.append({
                    "scan_id": scan_id,
                    "created_at": scan.created_at.isoformat() if scan.created_at else None,
                    "scan_type": scan.scan_type,
                    "anomaly_score": float(score),
                    "total_findings": scan.total_findings or 0,
                    "critical_count": scan.critical_count or 0,
                    "high_count": scan.high_count or 0,
                    "reason": self._explain_anomaly(features[i])
                })
        
        # Sort by anomaly score (most anomalous first)
        anomalies.sort(key=lambda x: x["anomaly_score"])
        
        return {
            "enabled": True,
            "anomalies": anomalies,
            "total_scans": len(scans),
            "anomaly_count": len(anomalies),
            "anomaly_rate": len(anomalies) / len(scans) if scans else 0,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()}
        }
    
    def _explain_anomaly(self, features: List[float]) -> str:
        """Generate human-readable explanation for an anomaly"""
        total_findings, critical_count, high_count, duration_ms, findings_per_second = features
        
        reasons = []
        if total_findings > 100:
            reasons.append("unusually high total findings")
        if critical_count > 10:
            reasons.append("unusually high critical findings")
        if high_count > 20:
            reasons.append("unusually high high-severity findings")
        if duration_ms > 300000:  # 5 minutes
            reasons.append("unusually long scan duration")
        if findings_per_second > 10:
            reasons.append("unusually high findings per second")
        
        return "; ".join(reasons) if reasons else "unusual pattern detected"
    
    def analyze_correlations(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Analyze correlations between finding patterns using Pearson correlation.
        This is statistical analysis, not ML training.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary with correlation analysis results
        """
        if not HAS_SKLEARN:
            return {
                "enabled": False,
                "message": "Correlation analysis requires scipy (part of scikit-learn dependencies)"
            }
        
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Query findings
        q_findings = self.db.query(Finding).join(Scan).filter(
            and_(
                Scan.tenant_id == self.tenant_id,
                Scan.created_at >= start_date,
                Scan.created_at <= end_date
            )
        )
        
        findings = q_findings.all()
        
        if len(findings) < 10:
            return {
                "enabled": True,
                "correlations": {},
                "message": "Insufficient data for correlation analysis (need at least 10 findings)"
            }
        
        # Build feature vectors: [severity_numeric, category_hash, scanner_hash]
        severity_map = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
        categories = {}
        scanners = {}
        
        severity_values = []
        category_values = []
        scanner_values = []
        
        for finding in findings:
            severity = (finding.severity or "low").lower()
            category = finding.category or "unknown"
            scanner = finding.scanner or "unknown"
            
            severity_values.append(severity_map.get(severity, 0))
            
            if category not in categories:
                categories[category] = len(categories)
            category_values.append(categories[category])
            
            if scanner not in scanners:
                scanners[scanner] = len(scanners)
            scanner_values.append(scanners[scanner])
        
        # Calculate Pearson correlations
        correlations = {}
        
        try:
            # Severity vs Category correlation
            if len(set(category_values)) > 1:
                corr, p_value = pearsonr(severity_values, category_values)
                correlations["severity_category"] = {
                    "correlation": float(corr),
                    "p_value": float(p_value),
                    "significant": p_value < 0.05
                }
            
            # Severity vs Scanner correlation
            if len(set(scanner_values)) > 1:
                corr, p_value = pearsonr(severity_values, scanner_values)
                correlations["severity_scanner"] = {
                    "correlation": float(corr),
                    "p_value": float(p_value),
                    "significant": p_value < 0.05
                }
            
            # Category vs Scanner correlation
            if len(set(category_values)) > 1 and len(set(scanner_values)) > 1:
                corr, p_value = pearsonr(category_values, scanner_values)
                correlations["category_scanner"] = {
                    "correlation": float(corr),
                    "p_value": float(p_value),
                    "significant": p_value < 0.05
                }
        except Exception as e:
            logger.error("correlation_analysis_failed", error=str(e))
        
        return {
            "enabled": True,
            "correlations": correlations,
            "total_findings": len(findings),
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()}
        }
    
    def prioritize_remediations(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Prioritize remediation recommendations using rule-based scoring.
        This is NOT ML-based - it uses deterministic rules.
        Formula: severity_weight × frequency × time_since_first_seen_factor
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary with prioritized remediation recommendations
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=90)
        
        # Severity weights
        severity_weights = {
            "critical": 10,
            "high": 5,
            "medium": 2,
            "low": 1,
            "info": 0
        }
        
        # Query findings grouped by category and severity
        q_findings = self.db.query(
            Finding.category,
            Finding.severity,
            func.min(Scan.created_at).label("first_seen"),
            func.count(Finding.id).label("frequency")
        ).join(Scan).filter(
            and_(
                Scan.tenant_id == self.tenant_id,
                Scan.created_at >= start_date,
                Scan.created_at <= end_date
            )
        ).group_by(Finding.category, Finding.severity)
        
        results = q_findings.all()
        
        recommendations = []
        
        for result in results:
            category = result.category or "unknown"
            severity = (result.severity or "low").lower()
            first_seen = result.first_seen
            frequency = result.frequency or 0
            
            # Calculate priority score
            severity_weight = severity_weights.get(severity, 1)
            
            # Time factor: older findings get higher priority (up to 2x multiplier)
            if first_seen:
                age_days = (end_date - first_seen).days
                time_factor = min(2.0, 1.0 + (age_days / 90))  # Max 2x for 90+ days old
            else:
                time_factor = 1.0
            
            priority_score = severity_weight * frequency * time_factor
            
            recommendations.append({
                "category": category,
                "severity": severity,
                "frequency": frequency,
                "first_seen": first_seen.isoformat() if first_seen else None,
                "age_days": (end_date - first_seen).days if first_seen else 0,
                "priority_score": round(priority_score, 2),
                "recommendation": f"Address {frequency} {severity}-severity finding(s) in category '{category}'"
            })
        
        # Sort by priority score (highest first)
        recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return {
            "enabled": True,
            "recommendations": recommendations[:20],  # Top 20
            "total_recommendations": len(recommendations),
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()}
        }


# Convenience functions
def detect_anomalies(
    db: Session,
    tenant_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Detect anomalies for a tenant"""
    if not ML_INSIGHTS_ENABLED:
        return {"enabled": False, "message": "ML insights are disabled"}
    
    engine = MLInsightsEngine(db, tenant_id)
    return engine.detect_anomalies(start_date, end_date)


def analyze_correlations(
    db: Session,
    tenant_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Analyze finding correlations for a tenant"""
    if not ML_INSIGHTS_ENABLED:
        return {"enabled": False, "message": "ML insights are disabled"}
    
    engine = MLInsightsEngine(db, tenant_id)
    return engine.analyze_correlations(start_date, end_date)


def prioritize_remediations(
    db: Session,
    tenant_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Get prioritized remediation recommendations for a tenant"""
    if not ML_INSIGHTS_ENABLED:
        return {"enabled": False, "message": "ML insights are disabled"}
    
    engine = MLInsightsEngine(db, tenant_id)
    return engine.prioritize_remediations(start_date, end_date)


def is_ml_insights_enabled() -> bool:
    """Check if ML insights are enabled"""
    return ML_INSIGHTS_ENABLED and HAS_SKLEARN

