# RetailFlow — Monitoring Evidence

## 1. Objective

This document provides concrete evidence that the RetailFlow monitoring stack is operational in the local demonstrator environment.

It complements:

```text
docs/MONITORING.md
```

`MONITORING.md` explains the monitoring architecture.  
`MONITORING_EVIDENCE.md` documents the observable proof points that can be reused during the Master thesis defense.

---

## 2. Evidence Summary

| Evidence | Status | Proof |
|---|---:|---|
| Prometheus is running | OK | `Prometheus Server is Ready.` |
| FastAPI target is scraped | OK | Prometheus target `retailflow-fastapi` is `up` |
| PostgreSQL exporter target is scraped | OK | Prometheus target `retailflow-postgres` is `up` |
| Prometheus alert rules are loaded | OK | Alert group `retailflow-platform-alerts` is visible |
| Alert rules are valid | OK | Each rule has `health=ok` |
| Grafana dashboards are provisioned | OK | Dashboards are returned by Grafana API |
| FastAPI exposes metrics | OK | `/metrics` exposes `http_requests_total` |
| PostgreSQL exporter exposes metrics | OK | `/metrics` exposes PostgreSQL exporter metrics |

---

## 3. Prometheus Readiness Evidence

### Command

```bash
curl -s http://localhost:9090/-/ready
```

### Observed output

```text
Prometheus Server is Ready.
```

### Interpretation

Prometheus is started and ready to evaluate scrape targets and alerting rules.

---

## 4. Prometheus Alert Rules Evidence

### Command

```bash
curl -s http://localhost:9090/api/v1/rules | python -c '
import json
import sys

data = json.load(sys.stdin)

for group in data["data"]["groups"]:
    print("Group:", group["name"])
    print("File:", group["file"])
    for rule in group["rules"]:
        print("-", rule["name"], "| state=" + rule["state"], "| health=" + rule["health"])
'
```

### Observed output

```text
Group: retailflow-platform-alerts
File: /etc/prometheus/rules/retailflow_alerts.yml
- RetailFlowFastAPIDown | state=inactive | health=ok
- RetailFlowPostgresExporterDown | state=inactive | health=ok
- RetailFlowHighFastAPIRequestLatency | state=inactive | health=ok
- RetailFlowFastAPIHighErrorRate | state=inactive | health=ok
- RetailFlowPostgresTooManyConnections | state=inactive | health=ok
```

### Interpretation

The alerting rules are correctly loaded from:

```text
/etc/prometheus/rules/retailflow_alerts.yml
```

The `health=ok` value proves that Prometheus can parse and evaluate the rules.  
The `inactive` state is expected because the platform is currently healthy and no alert condition is active.

---

## 5. Grafana Provisioning Evidence

### Command

```bash
curl -s http://localhost:3000/api/search \
  -u admin:admin \
  | python -m json.tool
```

### Observed dashboards

```text
RetailFlow API Overview
RetailFlow Platform Overview
```

### Observed folder

```text
RetailFlow
```

### Interpretation

Grafana is running and the dashboards are provisioned through the repository configuration.

The dashboards are available locally through Grafana:

```text
http://localhost:3000
```

Local demonstrator credentials:

```text
Username: admin
Password: admin
```

---

## 6. FastAPI Metrics Evidence

### Command

```bash
curl -s http://localhost:8000/metrics | head -n 40
```

### Observed metrics examples

```text
python_gc_objects_collected_total
python_info
process_virtual_memory_bytes
process_resident_memory_bytes
process_cpu_seconds_total
http_requests_total
```

Example observed application metric:

```text
http_requests_total{handler="/openapi.json",method="GET",status="2xx"} 730.0
http_requests_total{handler="/metrics",method="GET",status="2xx"} 491.0
```

### Interpretation

FastAPI exposes a Prometheus-compatible `/metrics` endpoint.

This proves that API-level monitoring is available, including HTTP request counters and Python process metrics.

---

## 7. PostgreSQL Exporter Metrics Evidence

### Command

```bash
curl -s http://localhost:9187/metrics | head -n 40
```

### Observed metrics examples

```text
go_gc_duration_seconds
go_goroutines
go_info
go_memstats_alloc_bytes
```

The exporter also provides PostgreSQL-specific metrics used by dashboards and alerts, such as:

```text
pg_up
pg_stat_activity_count
pg_database_size_bytes
```

### Interpretation

The PostgreSQL exporter is running and exposes Prometheus-compatible metrics.

This enables PostgreSQL monitoring through Prometheus and Grafana.

---

## 8. Grafana Dashboard Content Evidence

The dashboards are stored in:

```text
monitoring/grafana/dashboards/
```

Existing dashboard files:

```text
retailflow_api_overview.json
retailflow_platform_overview.json
```

### RetailFlow API Overview

This dashboard includes panels for:

| Panel | Prometheus Query |
|---|---|
| API Requests / min | `sum(rate(http_requests_total[1m])) * 60` |
| 5xx Errors | `sum(rate(http_requests_total{status=~"5.."}[5m]))` |
| Requests by Endpoint | `sum by (handler) (rate(http_requests_total[1m]))` |
| Latency p95 | `histogram_quantile(0.95, sum by (le, handler) (rate(http_request_duration_seconds_bucket[5m])))` |
| HTTP Status Codes | `sum by (status) (rate(http_requests_total[1m]))` |
| Python Memory Usage | `process_resident_memory_bytes` |

### RetailFlow Platform Overview

This dashboard includes panels for:

| Panel | Prometheus Query |
|---|---|
| FastAPI Up | `up{job="retailflow-fastapi"}` |
| PostgreSQL Up | `pg_up{job="retailflow-postgres"}` |
| API Requests / min | `sum(rate(http_requests_total[1m])) * 60` |
| PostgreSQL Connections | `sum(pg_stat_activity_count{job="retailflow-postgres"})` |
| API Requests by Endpoint | `sum by (handler) (rate(http_requests_total[1m]))` |
| API Latency p95 | `histogram_quantile(0.95, sum by (le, handler) (rate(http_request_duration_seconds_bucket[5m])))` |
| PostgreSQL Active Connections | `sum by (datname) (pg_stat_activity_count{job="retailflow-postgres"})` |
| PostgreSQL Database Size | `pg_database_size_bytes{job="retailflow-postgres", datname="retailflow_db"}` |
| Prometheus Targets Up | `up` |
| HTTP Status Codes | `sum by (status) (rate(http_requests_total[1m]))` |

---

## 9. Local URLs for Demonstration

| Tool | URL | Purpose |
|---|---|---|
| Prometheus | http://localhost:9090 | Targets, metrics, rules |
| Grafana | http://localhost:3000 | Dashboards |
| FastAPI metrics | http://localhost:8000/metrics | API metrics endpoint |
| PostgreSQL exporter metrics | http://localhost:9187/metrics | PostgreSQL metrics endpoint |

---

## 10. Defense Positioning

During the defense, this evidence can be presented as follows:

```text
RetailFlow includes an operational monitoring layer based on Prometheus, Grafana, and postgres_exporter.

Prometheus is ready, scrapes the FastAPI and PostgreSQL exporter targets, and evaluates a set of versioned alerting rules.
The alert rules are loaded from the repository and show health=ok, proving that they are valid and evaluated.

Grafana dashboards are automatically provisioned and expose both API-level and platform-level observability indicators.
FastAPI exposes HTTP and process metrics, while postgres_exporter exposes PostgreSQL metrics.

For the demonstrator, alerts are evaluated locally but are not routed to external notification channels.
This is an intentional design choice to keep the platform simple, reliable, and defensible for the Master thesis scope.
```

---

## 11. Current Limitations

The monitoring evidence is intentionally scoped to the local demonstrator.

Current limitations:

- no Alertmanager notification routing
- no external alert delivery channel
- no high-availability monitoring setup
- no long-term metrics storage
- no production-grade Grafana authentication
- no automated SLO or error budget management

These limitations are documented and can be presented as future production improvements.
