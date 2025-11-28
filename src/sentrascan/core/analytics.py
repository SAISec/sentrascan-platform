"""
Analytics Engine

Provides analytics and insights for scan data including:
- Trend analysis (findings over time)
- Severity distribution
- Scanner effectiveness metrics
- Remediation progress tracking
- Risk scoring and prioritization
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, Integer
from sentrascan.core.models import Scan, Finding
from sentrascan.core.query_helpers import filter_by_tenant
import structlog

logger = structlog.get_logger(__name__)


class AnalyticsEngine:
    """Analytics engine for processing scan and finding data"""
    
    def __init__(self, db: Session, tenant_id: str):
        """
        Initialize analytics engine.
        
        Args:
            db: Database session
            tenant_id: Tenant ID for data scoping
        """
        self.db = db
        self.tenant_id = tenant_id
    
    def get_trend_analysis(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "day"
    ) -> Dict[str, Any]:
        """
        Analyze findings trends over time.
        
        Args:
            start_date: Start date for analysis (defaults to 30 days ago)
            end_date: End date for analysis (defaults to now)
            group_by: Grouping interval ("day", "week", "month")
            
        Returns:
            Dictionary with trend data
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Query scans with findings
        q_scans = self.db.query(Scan).filter(
            and_(
                Scan.tenant_id == self.tenant_id,
                Scan.created_at >= start_date,
                Scan.created_at <= end_date
            )
        )
        
        scans = q_scans.all()
        
        if not scans:
            return {
                "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
                "group_by": group_by,
                "data": [],
                "summary": {
                    "total_scans": 0,
                    "total_findings": 0,
                    "avg_findings_per_scan": 0
                }
            }
        
        # Build DataFrame
        data = []
        for scan in scans:
            data.append({
                "date": scan.created_at,
                "scan_id": scan.id,
                "scan_type": scan.scan_type,
                "total_findings": scan.total_findings or 0,
                "critical_count": scan.critical_count or 0,
                "high_count": scan.high_count or 0,
                "medium_count": scan.medium_count or 0,
                "low_count": scan.low_count or 0,
                "passed": scan.passed
            })
        
        df = pd.DataFrame(data)
        
        # Group by time period
        if group_by == "day":
            df["period"] = df["date"].dt.date
        elif group_by == "week":
            df["period"] = df["date"].dt.to_period("W")
        elif group_by == "month":
            df["period"] = df["date"].dt.to_period("M")
        else:
            df["period"] = df["date"].dt.date
        
        # Aggregate by period
        grouped = df.groupby("period").agg({
            "total_findings": "sum",
            "critical_count": "sum",
            "high_count": "sum",
            "medium_count": "sum",
            "low_count": "sum",
            "scan_id": "count",
            "passed": lambda x: (x == True).sum()
        }).reset_index()
        
        grouped.columns = ["period", "total_findings", "critical_count", "high_count", "medium_count", "low_count", "scan_count", "passed_count"]
        
        # Convert period to string for JSON serialization
        grouped["period"] = grouped["period"].astype(str)
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "group_by": group_by,
            "data": grouped.to_dict("records"),
            "summary": {
                "total_scans": len(scans),
                "total_findings": int(df["total_findings"].sum()),
                "avg_findings_per_scan": float(df["total_findings"].mean()) if len(df) > 0 else 0,
                "pass_rate": float((df["passed"] == True).sum() / len(df)) if len(df) > 0 else 0
            }
        }
    
    def get_severity_distribution(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get severity distribution of findings.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary with severity distribution
        """
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
        
        if not findings:
            return {
                "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
                "distribution": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "info": 0
                },
                "total": 0
            }
        
        # Count by severity
        severity_counts = {}
        for finding in findings:
            severity = (finding.severity or "low").lower()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        total = len(findings)
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "distribution": {
                "critical": severity_counts.get("critical", 0),
                "high": severity_counts.get("high", 0),
                "medium": severity_counts.get("medium", 0),
                "low": severity_counts.get("low", 0),
                "info": severity_counts.get("info", 0)
            },
            "total": total,
            "percentages": {
                "critical": (severity_counts.get("critical", 0) / total * 100) if total > 0 else 0,
                "high": (severity_counts.get("high", 0) / total * 100) if total > 0 else 0,
                "medium": (severity_counts.get("medium", 0) / total * 100) if total > 0 else 0,
                "low": (severity_counts.get("low", 0) / total * 100) if total > 0 else 0,
                "info": (severity_counts.get("info", 0) / total * 100) if total > 0 else 0
            }
        }
    
    def get_scanner_effectiveness(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get scanner effectiveness metrics.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary with scanner effectiveness data
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Query scans grouped by scanner type
        q_scans = self.db.query(
            Scan.scan_type,
            func.count(Scan.id).label("scan_count"),
            func.sum(Scan.total_findings).label("total_findings"),
            func.sum(Scan.critical_count).label("critical_count"),
            func.sum(Scan.high_count).label("high_count"),
            func.sum(Scan.medium_count).label("medium_count"),
            func.sum(Scan.low_count).label("low_count"),
            func.avg(Scan.duration_ms).label("avg_duration_ms"),
            func.sum(func.cast(Scan.passed, Integer)).label("passed_count")
        ).filter(
            and_(
                Scan.tenant_id == self.tenant_id,
                Scan.created_at >= start_date,
                Scan.created_at <= end_date
            )
        ).group_by(Scan.scan_type)
        
        results = q_scans.all()
        
        scanner_data = {}
        for result in results:
            scanner_type = result.scan_type or "unknown"
            total_scans = result.scan_count or 0
            passed_count = result.passed_count or 0
            
            scanner_data[scanner_type] = {
                "scan_count": total_scans,
                "total_findings": int(result.total_findings or 0),
                "critical_count": int(result.critical_count or 0),
                "high_count": int(result.high_count or 0),
                "medium_count": int(result.medium_count or 0),
                "low_count": int(result.low_count or 0),
                "avg_duration_ms": float(result.avg_duration_ms or 0),
                "pass_rate": (passed_count / total_scans * 100) if total_scans > 0 else 0,
                "avg_findings_per_scan": (result.total_findings / total_scans) if total_scans > 0 else 0
            }
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "scanners": scanner_data
        }
    
    def get_remediation_progress(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Track remediation progress over time.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary with remediation progress data
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=90)
        
        # Query findings with their first seen date
        q_findings = self.db.query(
            Finding.severity,
            Finding.category,
            func.min(Scan.created_at).label("first_seen"),
            func.count(Finding.id).label("occurrence_count")
        ).join(Scan).filter(
            and_(
                Scan.tenant_id == self.tenant_id,
                Scan.created_at >= start_date,
                Scan.created_at <= end_date
            )
        ).group_by(Finding.severity, Finding.category)
        
        results = q_findings.all()
        
        # Calculate remediation metrics
        total_findings = sum(r.occurrence_count for r in results)
        findings_by_severity = {}
        findings_by_age = {
            "new": 0,  # < 7 days
            "recent": 0,  # 7-30 days
            "old": 0  # > 30 days
        }
        
        for result in results:
            severity = (result.severity or "low").lower()
            findings_by_severity[severity] = findings_by_severity.get(severity, 0) + result.occurrence_count
            
            # Calculate age
            if result.first_seen:
                age_days = (end_date - result.first_seen).days
                if age_days < 7:
                    findings_by_age["new"] += result.occurrence_count
                elif age_days < 30:
                    findings_by_age["recent"] += result.occurrence_count
                else:
                    findings_by_age["old"] += result.occurrence_count
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total_findings": total_findings,
            "by_severity": findings_by_severity,
            "by_age": findings_by_age,
            "remediation_rate": 0.0  # TODO: Calculate based on resolved findings
        }
    
    def get_risk_scores(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate risk scores and prioritization.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary with risk scores
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Query findings with severity weights
        severity_weights = {
            "critical": 10,
            "high": 5,
            "medium": 2,
            "low": 1,
            "info": 0
        }
        
        q_findings = self.db.query(Finding).join(Scan).filter(
            and_(
                Scan.tenant_id == self.tenant_id,
                Scan.created_at >= start_date,
                Scan.created_at <= end_date
            )
        )
        
        findings = q_findings.all()
        
        if not findings:
            return {
                "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
                "total_risk_score": 0,
                "by_severity": {},
                "top_risks": []
            }
        
        # Calculate risk scores
        risk_scores = {}
        total_risk = 0
        
        for finding in findings:
            severity = (finding.severity or "low").lower()
            weight = severity_weights.get(severity, 1)
            
            # Time decay factor (older findings have lower weight)
            age_days = (end_date - finding.created_at).days if finding.created_at else 0
            decay_factor = max(0.5, 1.0 - (age_days / 180))  # Decay over 180 days
            
            risk_score = weight * decay_factor
            total_risk += risk_score
            
            if severity not in risk_scores:
                risk_scores[severity] = 0
            risk_scores[severity] += risk_score
        
        # Get top risks by category
        category_risks = {}
        for finding in findings:
            category = finding.category or "unknown"
            severity = (finding.severity or "low").lower()
            weight = severity_weights.get(severity, 1)
            age_days = (end_date - finding.created_at).days if finding.created_at else 0
            decay_factor = max(0.5, 1.0 - (age_days / 180))
            risk_score = weight * decay_factor
            
            if category not in category_risks:
                category_risks[category] = 0
            category_risks[category] += risk_score
        
        top_risks = sorted(
            [{"category": k, "risk_score": v} for k, v in category_risks.items()],
            key=lambda x: x["risk_score"],
            reverse=True
        )[:10]
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total_risk_score": round(total_risk, 2),
            "by_severity": {k: round(v, 2) for k, v in risk_scores.items()},
            "top_risks": top_risks
        }


# Convenience functions
def get_trend_analysis(
    db: Session,
    tenant_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    group_by: str = "day"
) -> Dict[str, Any]:
    """Get trend analysis for a tenant"""
    engine = AnalyticsEngine(db, tenant_id)
    return engine.get_trend_analysis(start_date, end_date, group_by)


def get_severity_distribution(
    db: Session,
    tenant_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Get severity distribution for a tenant"""
    engine = AnalyticsEngine(db, tenant_id)
    return engine.get_severity_distribution(start_date, end_date)


def get_scanner_effectiveness(
    db: Session,
    tenant_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Get scanner effectiveness for a tenant"""
    engine = AnalyticsEngine(db, tenant_id)
    return engine.get_scanner_effectiveness(start_date, end_date)


def get_remediation_progress(
    db: Session,
    tenant_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Get remediation progress for a tenant"""
    engine = AnalyticsEngine(db, tenant_id)
    return engine.get_remediation_progress(start_date, end_date)


def get_risk_scores(
    db: Session,
    tenant_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Get risk scores for a tenant"""
    engine = AnalyticsEngine(db, tenant_id)
    return engine.get_risk_scores(start_date, end_date)

