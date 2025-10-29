# Prometheus Metrics + Alerts

## Overview

This repository implements monitoring and alerting for the MyESI API Gateway. It collects metrics from FastAPI and Redis, exposes them via Prometheus, and sends alerts using Alertmanager for specific conditions such as high error rates or rate limit violations.

Key capabilities:
- Collect API performance metrics (counts, latency, status codes)
- Collect Redis usage and health metrics
- Track and alert on HTTP 500 errors and failed requests
- Alert on rate-limit violations
- Expose metrics via a Prometheus-compatible endpoint: `/metrics`
- Centralized visualization via Grafana

---

## Features Implemented

- **API Performance Metrics**
  - Request counts
  - Request latency (histograms / summaries)
  - Status code breakdown (2xx, 4xx, 5xx)

- **Redis Metrics**
  - Redis exporter metrics (memory, connections, commands/sec, etc.)
  - Redis health/availability monitoring

- **Error Monitoring**
  - Detect and track HTTP 500s and other failed requests

- **Alerts**
  - Excessive HTTP 500 error rate
  - High rate-limit hits (clients exceeding configured limits)
  - Alerts evaluated by Prometheus and routed via Alertmanager

- **Prometheus Metrics Endpoint**
  - FastAPI exposes `/metrics` for Prometheus scraping

- **Dashboards**
  - Grafana dashboards to visualize latency, throughput, error rates, and Redis health

---

## Technology Stack

| Tool | Purpose |
|------|---------|
| Prometheus | Collects service metrics from FastAPI and Redis; evaluates alerting rules |
| Alertmanager | Receives alerts from Prometheus and dispatches notifications (email, Slack, etc.) |
| FastAPI instrumentation | Exposes runtime metrics such as response time and status codes on `/metrics` |
| Redis Exporter | Exposes Redis performance and usage metrics to Prometheus |
| Docker Compose | Orchestrates FastAPI, Redis, Redis Exporter, Prometheus, Alertmanager, (and optionally Grafana) |

---

## Architecture

FastAPI (API Gateway)
    │
    ├─ exposes `/metrics` → Prometheus scrapes it
    │
Redis
    ├─ monitored via Redis Exporter → Prometheus scrapes metrics
    │
Prometheus
    ├─ collects metrics from FastAPI and Redis
    ├─ evaluates alert rules
    └─ sends alerts to Alertmanager

Alertmanager
    └─ receives alerts from Prometheus and can notify via configured channels (e.g., email, Slack)

Grafana (optional)
    └─ visualizes metrics collected in Prometheus (dashboards for latency, errors, Redis, etc.)

---

## Docker Compose Setup

Start all services:
```bash
docker-compose up -d
```

Services and default ports:

| Service | Port |
|---------|------|
| FastAPI App | 8000 |
| Redis | 6379 |
| Redis Exporter | 9121 |
| Prometheus | 9090 |
| Alertmanager | 9093 |
| Grafana (optional) | 3000 |

Note: Ports may be configured differently in your `docker-compose.yml`. Check that file if you see different values.

---

## Prometheus & Alertmanager Configuration

Prometheus loads scraping targets and alerting rules from the monitoring configuration directory.

- monitoring/prometheus.yml → scrape targets (FastAPI `/metrics`, Redis Exporter)
- monitoring/alert_rules.yml → alert definitions (HTTP 500 spikes, rate-limit breaches)
- monitoring/alertmanager.yml → Alertmanager routing and notification channels (email, Slack, etc.)

Example Prometheus scrape target snippets (for reference):
```yaml
scrape_configs:
  - job_name: 'myesi-api'
    static_configs:
      - targets: ['fastapi:8000']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

Example alert rule descriptions (stored in `monitoring/alert_rules.yml`):
- High HTTP 500 error rate over a sustained period
- Frequent rate-limit hits from clients
- Redis down or memory/connection thresholds exceeded

---

## How to Test

1. Access the FastAPI application:
```bash
curl http://localhost:8000/
```

2. Check Prometheus targets and scrape health:
- Prometheus Targets: http://localhost:9090/targets
- Prometheus Graph / Query UI: http://localhost:9090/graph

3. Check Alertmanager UI:
- http://localhost:9093

4. Trigger alerts:
- Generate many failing requests (HTTP 500) to the API to trigger the "excessive HTTP 500" alert.
- Exceed configured rate limits by repeatedly calling endpoints to trigger rate-limit alerts.
- Monitor Alertmanager to see incoming alerts and their routing/notifications.

  ## Will show the following output in VS code if working properly 
C:\Users\HP\VS_projects\Prometheus_Metrics_Alerts> python -m uvicorn main:app --reload      

INFO:     Will watch for changes in these directories: ['C:\\Users\\HP\\VS_projects\\Prometheus_Metrics_Alerts']        
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [18476] using WatchFiles
INFO:     Started server process [21432]
INFO:     Waiting for application startup.
2025-10-28T19:19:22.967692+0500 | INFO | {'event': 'startup', 'msg': 'Redis client initialized'}
INFO:     Application startup complete.

