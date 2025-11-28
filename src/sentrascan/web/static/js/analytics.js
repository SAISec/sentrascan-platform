/**
 * Analytics Dashboard JavaScript
 * Handles loading and displaying analytics data with Chart.js
 */

const API_BASE = window.location.origin;
let currentDays = 30;
let charts = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadAnalytics();
    
    // Time range selector
    document.getElementById('time-range').addEventListener('change', function() {
        if (this.value === 'custom') {
            // TODO: Implement custom date range picker
            alert('Custom date range not yet implemented. Please select a predefined range.');
            this.value = '30';
        }
        currentDays = parseInt(this.value);
        loadAnalytics();
    });
});

// Load all analytics data
async function loadAnalytics() {
    try {
        // Load all analytics endpoints in parallel
        const [trends, severity, scanner, remediation, risk] = await Promise.all([
            fetch(`${API_BASE}/api/v1/analytics/trends?days=${currentDays}`, { credentials: 'include' }).then(r => r.json()),
            fetch(`${API_BASE}/api/v1/analytics/severity-distribution?days=${currentDays}`, { credentials: 'include' }).then(r => r.json()),
            fetch(`${API_BASE}/api/v1/analytics/scanner-effectiveness?days=${currentDays}`, { credentials: 'include' }).then(r => r.json()),
            fetch(`${API_BASE}/api/v1/analytics/remediation-progress?days=${currentDays}`, { credentials: 'include' }).then(r => r.json()),
            fetch(`${API_BASE}/api/v1/analytics/risk-scores?days=${currentDays}`, { credentials: 'include' }).then(r => r.json())
        ]);
        
        // Update summary statistics
        updateSummaryStats(trends, risk);
        
        // Render charts
        renderTrendChart(trends);
        renderSeverityChart(severity);
        renderScannerChart(scanner);
        renderRemediationChart(remediation);
        renderRiskChart(risk);
        
        // Load ML insights if enabled
        loadMLInsights();
    } catch (error) {
        console.error('Error loading analytics:', error);
        showToast('Failed to load analytics data', 'error');
    }
}

// Update summary statistics
function updateSummaryStats(trends, risk) {
    const summary = trends.summary || {};
    document.getElementById('stat-total-scans').textContent = summary.total_scans || 0;
    document.getElementById('stat-total-findings').textContent = summary.total_findings || 0;
    document.getElementById('stat-pass-rate').textContent = summary.pass_rate ? `${(summary.pass_rate * 100).toFixed(1)}%` : '-';
    document.getElementById('stat-risk-score').textContent = risk.total_risk_score ? risk.total_risk_score.toFixed(2) : '-';
}

// Render trend chart
function renderTrendChart(data) {
    const ctx = document.getElementById('trend-chart').getContext('2d');
    
    if (charts.trend) {
        charts.trend.destroy();
    }
    
    const trendData = data.data || [];
    charts.trend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: trendData.map(d => d.period),
            datasets: [
                {
                    label: 'Total Findings',
                    data: trendData.map(d => d.total_findings),
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                },
                {
                    label: 'Critical',
                    data: trendData.map(d => d.critical_count),
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1
                },
                {
                    label: 'High',
                    data: trendData.map(d => d.high_count),
                    borderColor: 'rgb(255, 159, 64)',
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    tension: 0.1
                },
                {
                    label: 'Medium',
                    data: trendData.map(d => d.medium_count),
                    borderColor: 'rgb(255, 205, 86)',
                    backgroundColor: 'rgba(255, 205, 86, 0.2)',
                    tension: 0.1
                },
                {
                    label: 'Low',
                    data: trendData.map(d => d.low_count),
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Render severity distribution chart
function renderSeverityChart(data) {
    const ctx = document.getElementById('severity-chart').getContext('2d');
    
    if (charts.severity) {
        charts.severity.destroy();
    }
    
    const distribution = data.distribution || {};
    charts.severity = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
            datasets: [{
                data: [
                    distribution.critical || 0,
                    distribution.high || 0,
                    distribution.medium || 0,
                    distribution.low || 0,
                    distribution.info || 0
                ],
                backgroundColor: [
                    'rgb(255, 99, 132)',
                    'rgb(255, 159, 64)',
                    'rgb(255, 205, 86)',
                    'rgb(54, 162, 235)',
                    'rgb(153, 102, 255)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true
        }
    });
}

// Render scanner effectiveness chart
function renderScannerChart(data) {
    const ctx = document.getElementById('scanner-chart').getContext('2d');
    
    if (charts.scanner) {
        charts.scanner.destroy();
    }
    
    const scanners = data.scanners || {};
    const scannerTypes = Object.keys(scanners);
    
    charts.scanner = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: scannerTypes,
            datasets: [
                {
                    label: 'Scan Count',
                    data: scannerTypes.map(s => scanners[s].scan_count || 0),
                    backgroundColor: 'rgba(54, 162, 235, 0.5)'
                },
                {
                    label: 'Total Findings',
                    data: scannerTypes.map(s => scanners[s].total_findings || 0),
                    backgroundColor: 'rgba(255, 99, 132, 0.5)'
                },
                {
                    label: 'Pass Rate (%)',
                    data: scannerTypes.map(s => scanners[s].pass_rate || 0),
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// Render remediation progress chart
function renderRemediationChart(data) {
    const ctx = document.getElementById('remediation-chart').getContext('2d');
    
    if (charts.remediation) {
        charts.remediation.destroy();
    }
    
    const byAge = data.by_age || {};
    charts.remediation = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['New (< 7 days)', 'Recent (7-30 days)', 'Old (> 30 days)'],
            datasets: [{
                label: 'Findings by Age',
                data: [
                    byAge.new || 0,
                    byAge.recent || 0,
                    byAge.old || 0
                ],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(255, 159, 64, 0.5)',
                    'rgba(255, 205, 86, 0.5)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Render risk scores chart
function renderRiskChart(data) {
    const ctx = document.getElementById('risk-chart').getContext('2d');
    
    if (charts.risk) {
        charts.risk.destroy();
    }
    
    const bySeverity = data.by_severity || {};
    charts.risk = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(bySeverity).map(s => s.charAt(0).toUpperCase() + s.slice(1)),
            datasets: [{
                label: 'Risk Score',
                data: Object.values(bySeverity),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(255, 159, 64, 0.5)',
                    'rgba(255, 205, 86, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(153, 102, 255, 0.5)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Export analytics
function exportAnalytics(format) {
    const url = `${API_BASE}/api/v1/analytics/export?format=${format}&days=${currentDays}`;
    window.open(url, '_blank');
}

// Load ML insights (if enabled)
async function loadMLInsights() {
    try {
        // Check if ML features are enabled
        const response = await fetch(`${API_BASE}/api/v1/ml-insights/status`, { credentials: 'include' });
        if (!response.ok) {
            // ML features not enabled
            return;
        }
        
        const status = await response.json();
        if (!status.enabled) {
            return;
        }
        
        // Load ML insights
        const insights = await fetch(`${API_BASE}/api/v1/ml-insights?days=${currentDays}`, { credentials: 'include' }).then(r => r.json());
        
        // Show ML insights panel
        const panel = document.getElementById('ml-insights-panel');
        panel.classList.remove('hidden');
        
        // Render ML insights
        renderMLInsights(insights);
    } catch (error) {
        // ML features not available or not enabled
        console.debug('ML insights not available:', error);
    }
}

// Render ML insights
function renderMLInsights(insights) {
    const content = document.getElementById('ml-insights-content');
    
    if (!insights.enabled) {
        content.innerHTML = `<p style="color: var(--color-text-secondary);">${insights.message || 'ML insights are not enabled'}</p>`;
        return;
    }
    
    let html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: var(--spacing-md);">';
    
    // Anomaly Detection
    if (insights.anomaly_detection && insights.anomaly_detection.enabled) {
        const anomalies = insights.anomaly_detection;
        html += `
            <div class="ml-insight-card" style="background: var(--color-bg-primary); border: 1px solid var(--color-border-light); border-radius: var(--radius-md); padding: var(--spacing-md);">
                <h3 style="margin: 0 0 var(--spacing-sm) 0; font-size: var(--font-size-lg);">Anomaly Detection</h3>
                <p style="margin: 0 0 var(--spacing-sm) 0; color: var(--color-text-secondary); font-size: var(--font-size-sm);">
                    ${anomalies.anomaly_count || 0} anomalies detected out of ${anomalies.total_scans || 0} scans
                </p>
                ${anomalies.anomalies && anomalies.anomalies.length > 0 ? `
                    <ul style="margin: var(--spacing-sm) 0 0 0; padding-left: var(--spacing-md); font-size: var(--font-size-sm);">
                        ${anomalies.anomalies.slice(0, 5).map(a => `
                            <li style="margin-bottom: var(--spacing-xs);">
                                <strong>${a.scan_type}</strong>: ${a.reason || 'Anomaly detected'}
                            </li>
                        `).join('')}
                    </ul>
                ` : '<p style="margin: var(--spacing-sm) 0 0 0; color: var(--color-text-secondary); font-size: var(--font-size-sm);">No anomalies detected</p>'}
            </div>
        `;
    }
    
    // Correlations
    if (insights.correlations && insights.correlations.enabled) {
        const correlations = insights.correlations;
        html += `
            <div class="ml-insight-card" style="background: var(--color-bg-primary); border: 1px solid var(--color-border-light); border-radius: var(--radius-md); padding: var(--spacing-md);">
                <h3 style="margin: 0 0 var(--spacing-sm) 0; font-size: var(--font-size-lg);">Finding Correlations</h3>
                <p style="margin: 0 0 var(--spacing-sm) 0; color: var(--color-text-secondary); font-size: var(--font-size-sm);">
                    ${Object.keys(correlations.correlations || {}).length} correlation(s) analyzed
                </p>
                ${Object.keys(correlations.correlations || {}).length > 0 ? `
                    <ul style="margin: var(--spacing-sm) 0 0 0; padding-left: var(--spacing-md); font-size: var(--font-size-sm);">
                        ${Object.entries(correlations.correlations).map(([key, value]) => `
                            <li style="margin-bottom: var(--spacing-xs);">
                                <strong>${key.replace('_', ' ')}</strong>: ${value.correlation.toFixed(3)} 
                                ${value.significant ? '<span style="color: var(--color-success);">(significant)</span>' : ''}
                            </li>
                        `).join('')}
                    </ul>
                ` : '<p style="margin: var(--spacing-sm) 0 0 0; color: var(--color-text-secondary); font-size: var(--font-size-sm);">No significant correlations found</p>'}
            </div>
        `;
    }
    
    // Remediation Prioritization
    if (insights.remediation_prioritization && insights.remediation_prioritization.enabled) {
        const remediations = insights.remediation_prioritization;
        html += `
            <div class="ml-insight-card" style="background: var(--color-bg-primary); border: 1px solid var(--color-border-light); border-radius: var(--radius-md); padding: var(--spacing-md);">
                <h3 style="margin: 0 0 var(--spacing-sm) 0; font-size: var(--font-size-lg);">Remediation Priorities</h3>
                <p style="margin: 0 0 var(--spacing-sm) 0; color: var(--color-text-secondary); font-size: var(--font-size-sm);">
                    Top ${remediations.recommendations?.length || 0} recommendations
                </p>
                ${remediations.recommendations && remediations.recommendations.length > 0 ? `
                    <ul style="margin: var(--spacing-sm) 0 0 0; padding-left: var(--spacing-md); font-size: var(--font-size-sm);">
                        ${remediations.recommendations.slice(0, 5).map(r => `
                            <li style="margin-bottom: var(--spacing-xs);">
                                <strong>Priority ${r.priority_score}</strong>: ${r.recommendation}
                            </li>
                        `).join('')}
                    </ul>
                ` : '<p style="margin: var(--spacing-sm) 0 0 0; color: var(--color-text-secondary); font-size: var(--font-size-sm);">No recommendations available</p>'}
            </div>
        `;
    }
    
    html += '</div>';
    content.innerHTML = html;
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-3 rounded-md shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

