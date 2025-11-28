"""
Analytics Export Module

Provides export functionality for analytics data in CSV, JSON, and PDF formats.
"""

import csv
import json
import io
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

import structlog

logger = structlog.get_logger(__name__)


def export_trends_csv(trend_data: Dict[str, Any]) -> str:
    """Export trend analysis data as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Period", "Total Findings", "Critical", "High", "Medium", "Low", "Scan Count", "Passed Count"])
    
    # Data rows
    for row in trend_data.get("data", []):
        writer.writerow([
            row.get("period", ""),
            row.get("total_findings", 0),
            row.get("critical_count", 0),
            row.get("high_count", 0),
            row.get("medium_count", 0),
            row.get("low_count", 0),
            row.get("scan_count", 0),
            row.get("passed_count", 0)
        ])
    
    # Summary
    writer.writerow([])
    writer.writerow(["Summary"])
    summary = trend_data.get("summary", {})
    writer.writerow(["Total Scans", summary.get("total_scans", 0)])
    writer.writerow(["Total Findings", summary.get("total_findings", 0)])
    writer.writerow(["Avg Findings per Scan", f"{summary.get('avg_findings_per_scan', 0):.2f}"])
    writer.writerow(["Pass Rate", f"{summary.get('pass_rate', 0) * 100:.2f}%"])
    
    output.seek(0)
    return output.getvalue()


def export_severity_distribution_csv(severity_data: Dict[str, Any]) -> str:
    """Export severity distribution data as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Severity", "Count", "Percentage"])
    
    # Data rows
    distribution = severity_data.get("distribution", {})
    percentages = severity_data.get("percentages", {})
    total = severity_data.get("total", 0)
    
    for severity in ["critical", "high", "medium", "low", "info"]:
        count = distribution.get(severity, 0)
        pct = percentages.get(severity, 0)
        writer.writerow([severity.capitalize(), count, f"{pct:.2f}%"])
    
    writer.writerow(["Total", total, "100.00%"])
    
    output.seek(0)
    return output.getvalue()


def export_scanner_effectiveness_csv(scanner_data: Dict[str, Any]) -> str:
    """Export scanner effectiveness data as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Scanner", "Scan Count", "Total Findings", "Critical", "High", "Medium", "Low", "Avg Duration (ms)", "Pass Rate (%)", "Avg Findings per Scan"])
    
    # Data rows
    scanners = scanner_data.get("scanners", {})
    for scanner_type, metrics in scanners.items():
        writer.writerow([
            scanner_type,
            metrics.get("scan_count", 0),
            metrics.get("total_findings", 0),
            metrics.get("critical_count", 0),
            metrics.get("high_count", 0),
            metrics.get("medium_count", 0),
            metrics.get("low_count", 0),
            f"{metrics.get('avg_duration_ms', 0):.2f}",
            f"{metrics.get('pass_rate', 0):.2f}",
            f"{metrics.get('avg_findings_per_scan', 0):.2f}"
        ])
    
    output.seek(0)
    return output.getvalue()


def export_remediation_progress_csv(remediation_data: Dict[str, Any]) -> str:
    """Export remediation progress data as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Metric", "Value"])
    
    # Data rows
    writer.writerow(["Total Findings", remediation_data.get("total_findings", 0)])
    writer.writerow(["Remediation Rate", f"{remediation_data.get('remediation_rate', 0) * 100:.2f}%"])
    
    writer.writerow([])
    writer.writerow(["By Severity"])
    by_severity = remediation_data.get("by_severity", {})
    for severity, count in by_severity.items():
        writer.writerow([severity.capitalize(), count])
    
    writer.writerow([])
    writer.writerow(["By Age"])
    by_age = remediation_data.get("by_age", {})
    for age, count in by_age.items():
        writer.writerow([age.capitalize(), count])
    
    output.seek(0)
    return output.getvalue()


def export_risk_scores_csv(risk_data: Dict[str, Any]) -> str:
    """Export risk scores data as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Metric", "Value"])
    
    # Data rows
    writer.writerow(["Total Risk Score", f"{risk_data.get('total_risk_score', 0):.2f}"])
    
    writer.writerow([])
    writer.writerow(["By Severity"])
    by_severity = risk_data.get("by_severity", {})
    for severity, score in by_severity.items():
        writer.writerow([severity.capitalize(), f"{score:.2f}"])
    
    writer.writerow([])
    writer.writerow(["Top Risks by Category"])
    writer.writerow(["Category", "Risk Score"])
    top_risks = risk_data.get("top_risks", [])
    for risk in top_risks:
        writer.writerow([risk.get("category", ""), f"{risk.get('risk_score', 0):.2f}"])
    
    output.seek(0)
    return output.getvalue()


def export_analytics_pdf(
    trend_data: Optional[Dict[str, Any]] = None,
    severity_data: Optional[Dict[str, Any]] = None,
    scanner_data: Optional[Dict[str, Any]] = None,
    remediation_data: Optional[Dict[str, Any]] = None,
    risk_data: Optional[Dict[str, Any]] = None,
    tenant_name: str = "Unknown"
) -> bytes:
    """Export analytics data as PDF"""
    if not HAS_PDF:
        raise ValueError("PDF export requires reportlab. Install with: pip install reportlab")
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
    )
    story.append(Paragraph(f"Analytics Report - {tenant_name}", title_style))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Trend Analysis
    if trend_data:
        story.append(Paragraph("Trend Analysis", styles['Heading2']))
        summary = trend_data.get("summary", {})
        trend_table_data = [
            ["Metric", "Value"],
            ["Total Scans", str(summary.get("total_scans", 0))],
            ["Total Findings", str(summary.get("total_findings", 0))],
            ["Avg Findings per Scan", f"{summary.get('avg_findings_per_scan', 0):.2f}"],
            ["Pass Rate", f"{summary.get('pass_rate', 0) * 100:.2f}%"]
        ]
        trend_table = Table(trend_table_data, colWidths=[3*inch, 2*inch])
        trend_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(trend_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Severity Distribution
    if severity_data:
        story.append(Paragraph("Severity Distribution", styles['Heading2']))
        distribution = severity_data.get("distribution", {})
        percentages = severity_data.get("percentages", {})
        severity_table_data = [["Severity", "Count", "Percentage"]]
        for severity in ["critical", "high", "medium", "low", "info"]:
            count = distribution.get(severity, 0)
            pct = percentages.get(severity, 0)
            severity_table_data.append([severity.capitalize(), str(count), f"{pct:.2f}%"])
        
        severity_table = Table(severity_table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        severity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(severity_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Scanner Effectiveness
    if scanner_data:
        story.append(Paragraph("Scanner Effectiveness", styles['Heading2']))
        scanners = scanner_data.get("scanners", {})
        scanner_table_data = [["Scanner", "Scans", "Findings", "Pass Rate"]]
        for scanner_type, metrics in scanners.items():
            scanner_table_data.append([
                scanner_type,
                str(metrics.get("scan_count", 0)),
                str(metrics.get("total_findings", 0)),
                f"{metrics.get('pass_rate', 0):.2f}%"
            ])
        
        scanner_table = Table(scanner_table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch])
        scanner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(scanner_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Risk Scores
    if risk_data:
        story.append(Paragraph("Risk Scores", styles['Heading2']))
        risk_table_data = [["Metric", "Value"]]
        risk_table_data.append(["Total Risk Score", f"{risk_data.get('total_risk_score', 0):.2f}"])
        by_severity = risk_data.get("by_severity", {})
        for severity, score in by_severity.items():
            risk_table_data.append([f"{severity.capitalize()} Risk", f"{score:.2f}"])
        
        risk_table = Table(risk_table_data, colWidths=[3*inch, 2*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(risk_table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def export_analytics_json(
    trend_data: Optional[Dict[str, Any]] = None,
    severity_data: Optional[Dict[str, Any]] = None,
    scanner_data: Optional[Dict[str, Any]] = None,
    remediation_data: Optional[Dict[str, Any]] = None,
    risk_data: Optional[Dict[str, Any]] = None
) -> str:
    """Export analytics data as JSON"""
    export_data = {
        "exported_at": datetime.utcnow().isoformat(),
        "analytics": {}
    }
    
    if trend_data:
        export_data["analytics"]["trends"] = trend_data
    if severity_data:
        export_data["analytics"]["severity_distribution"] = severity_data
    if scanner_data:
        export_data["analytics"]["scanner_effectiveness"] = scanner_data
    if remediation_data:
        export_data["analytics"]["remediation_progress"] = remediation_data
    if risk_data:
        export_data["analytics"]["risk_scores"] = risk_data
    
    return json.dumps(export_data, indent=2)

