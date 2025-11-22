# Monitoring Guide

Complete guide for monitoring SentraScan Platform in production.

## Table of Contents

1. [Metrics to Monitor](#metrics-to-monitor)
2. [Prometheus Setup](#prometheus-setup)
3. [Grafana Dashboards](#grafana-dashboards)
4. [Alerting](#alerting)
5. [Log Management](#log-management)

---

## Metrics to Monitor

### Key Performance Indicators (KPIs)

**Scan Metrics:**
- Total scans per day/hour
- Scan success rate
- Average scan duration (P50, P95, P99)
- Failed scans count
- Findings distribution by severity

**System Metrics:**
- API response time (P50, P95, P99)
- Database query performance
- CPU usage
- Memory usage
- Disk I/O
- Network throughput

**Business Metrics:**
- Scans blocked by policy
- Critical findings detected
- Baseline drift incidents
- API key usage

### Health Checks

```bash
# API Health
curl http://localhost:8200/api/v1/health

# Database Health
docker-compose exec db psql -U sentrascan -d sentrascan -c "SELECT 1;"

# Scanner Health
docker-compose exec api sentrascan doctor
```

---

## Prometheus Setup

### Exporter Endpoint

Add metrics endpoint to `server.py`:

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# Metrics
scan_counter = Counter('sentrascan_scans_total', 'Total scans', ['type', 'status'])
scan_duration = Histogram('sentrascan_scan_duration_seconds', 'Scan duration', ['type'])
active_scans = Gauge('sentrascan_active_scans', 'Active scans')
findings_total = Counter('sentrascan_findings_total', 'Total findings', ['severity'])

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
```

### Prometheus Configuration

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'sentrascan'
    static_configs:
      - targets: ['api:8200']
    metrics_path: '/metrics'
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

### Docker Compose

```yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter
    environment:
      - DATA_SOURCE_NAME=postgresql://sentrascan:password@db:5432/sentrascan?sslmode=disable
    ports:
      - "9187:9187"
```

---

## Grafana Dashboards

### Dashboard JSON

```json
{
  "dashboard": {
    "title": "SentraScan Platform",
    "panels": [
      {
        "title": "Scans per Hour",
        "targets": [{
          "expr": "rate(sentrascan_scans_total[1h])"
        }]
      },
      {
        "title": "Scan Duration (P95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, sentrascan_scan_duration_seconds_bucket)"
        }]
      },
      {
        "title": "Failed Scans",
        "targets": [{
          "expr": "sentrascan_scans_total{status=\"failed\"}"
        }]
      },
      {
        "title": "Findings by Severity",
        "targets": [{
          "expr": "sentrascan_findings_total"
        }]
      }
    ]
  }
}
```

### Key Queries

**Scan Rate:**
```promql
rate(sentrascan_scans_total[5m])
```

**Error Rate:**
```promql
rate(sentrascan_scans_total{status="failed"}[5m])
```

**P95 Scan Duration:**
```promql
histogram_quantile(0.95, sentrascan_scan_duration_seconds_bucket)
```

**Active Scans:**
```promql
sentrascan_active_scans
```

---

## Alerting

### Alert Rules

Create `alerts.yml`:

```yaml
groups:
  - name: sentrascan
    rules:
      - alert: HighErrorRate
        expr: rate(sentrascan_scans_total{status="failed"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High scan failure rate"
          
      - alert: SlowScans
        expr: histogram_quantile(0.95, sentrascan_scan_duration_seconds_bucket) > 60
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Scans are taking too long"
          
      - alert: APIDown
        expr: up{job="sentrascan"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "SentraScan API is down"
          
      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database is down"
```

### Alertmanager Configuration

```yaml
route:
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
```

---

## Log Management

### Structured Logging

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if hasattr(record, "scan_id"):
            log_entry["scan_id"] = record.scan_id
        return json.dumps(log_entry)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)
```

### Log Aggregation

**ELK Stack:**

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    environment:
      - discovery.type=single-node
    volumes:
      - es-data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.0.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
    ports:
      - "5601:5601"
```

**Logstash Configuration:**

```ruby
input {
  docker {
    codec => json
  }
}

filter {
  if [container_name] == "sentrascan-api" {
    json {
      source => "message"
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "sentrascan-%{+YYYY.MM.dd}"
  }
}
```

---

## Custom Metrics

### Application Metrics

```python
from prometheus_client import Counter, Histogram

# Custom metrics
api_requests = Counter('api_requests_total', 'API requests', ['method', 'endpoint', 'status'])
api_duration = Histogram('api_request_duration_seconds', 'API request duration', ['endpoint'])

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    api_requests.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    api_duration.labels(endpoint=request.url.path).observe(duration)
    
    return response
```

---

## Next Steps

**Operations:**
- [Runbooks](RUNBOOKS.md) - Operational procedures and health checks
- [Administrator Guide](ADMIN-GUIDE.md) - Production deployment
- [Backup & Recovery](BACKUP-RECOVERY.md) - Backup and recovery procedures

**Reference:**
- [Technical Documentation](TECHNICAL-DOCUMENTATION.md) - Technical details
- [Documentation Index](README.md) - Complete documentation overview

---

**Monitoring Support:** [Your monitoring contact]

