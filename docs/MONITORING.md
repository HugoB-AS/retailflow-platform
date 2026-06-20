# RetailFlow — Monitoring and Observability

## 1. Objective

RetailFlow includes a lightweight observability stack to monitor the technical health of the platform.

The objective is to provide visibility on:

- FastAPI availability and latency
- PostgreSQL exporter availability
- PostgreSQL connection pressure
- Prometheus scraping status
- Grafana dashboards for visual monitoring
- Alerting rules that can support a future production-grade monitoring strategy

This setup is designed for a Master thesis demonstrator. It provides operational evidence without pretending to be a fully redundant production monitoring platform.

---

## 2. Monitoring Stack

The monitoring stack is composed of:

| Component | Role | Local URL |
|---|---|---|
| Prometheus | Metrics collection and alert rule evaluation | http://localhost:9090 |
| Grafana | Dashboard visualization | http://localhost:3000 |
| postgres_exporter | PostgreSQL metrics exporter | http://localhost:9187 |
| FastAPI `/metrics` | API metrics endpoint | http://localhost:8000/metrics |

Grafana credentials for the local demonstrator:

```text
Username: admin
Password: admin
```

---

## 3. Prometheus Configuration

Prometheus configuration is stored in:

```text
monitoring/prometheus/prometheus.yml
```

It currently scrapes:

```text
retailflow-fastapi
retailflow-postgres
```

The configuration also loads alerting rules from:

```text
/etc/prometheus/rules/*.yml
```

The local Docker Compose file mounts the rules directory:

```text
./monitoring/prometheus/rules:/etc/prometheus/rules
```

---

## 4. Alerting Rules

Alerting rules are stored in:

```text
monitoring/prometheus/rules/retailflow_alerts.yml
```

The current alert group is:

```text
retailflow-platform-alerts
```

Configured alerts:

| Alert | Severity | Component | Purpose |
|---|---|---|---|
| RetailFlowFastAPIDown | critical | FastAPI | Detects when FastAPI metrics cannot be scraped |
| RetailFlowPostgresExporterDown | critical | PostgreSQL | Detects when postgres_exporter cannot be scraped |
| RetailFlowHighFastAPIRequestLatency | warning | FastAPI | Detects high p95 API latency |
| RetailFlowFastAPIHighErrorRate | warning | FastAPI | Detects HTTP 5xx errors |
| RetailFlowPostgresTooManyConnections | warning | PostgreSQL | Detects high PostgreSQL connection count |

These alerts are currently evaluated by Prometheus. They are not connected to an external notification system such as email, Slack, PagerDuty, or Alertmanager.

This is intentional for the demonstrator: the project proves that alert rules exist, are loaded, and are evaluated, while avoiding unnecessary operational complexity.

---

## 5. Verification Commands

### Check Prometheus readiness

```bash
curl -s http://localhost:9090/-/ready
```

Expected output:

```text
Prometheus Server is Ready.
```

### Check Prometheus targets

```bash
curl -s http://localhost:9090/api/v1/targets
```

Expected target status:

```text
retailflow-fastapi = up
retailflow-postgres = up
```

### Check loaded alerting rules

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

Expected output:

```text
Group: retailflow-platform-alerts
File: /etc/prometheus/rules/retailflow_alerts.yml
- RetailFlowFastAPIDown | state=inactive | health=ok
- RetailFlowPostgresExporterDown | state=inactive | health=ok
- RetailFlowHighFastAPIRequestLatency | state=inactive | health=ok
- RetailFlowFastAPIHighErrorRate | state=inactive | health=ok
- RetailFlowPostgresTooManyConnections | state=inactive | health=ok
```

The `inactive` state means that the alert condition is not currently true.  
The `health=ok` value means that Prometheus can evaluate the rule correctly.

---

## 6. Grafana Dashboards

Grafana provisioning files are stored in:

```text
monitoring/grafana/provisioning/
```

Dashboard JSON files are stored in:

```text
monitoring/grafana/dashboards/
```

Existing dashboards:

```text
retailflow_api_overview.json
retailflow_platform_overview.json
```

These dashboards provide visual evidence of platform observability for the local demonstrator.

---

## 7. Docker Compose Integration

The monitoring services are defined in:

```text
docker-compose.yml
```

Relevant services:

```text
prometheus
grafana
postgres_exporter
```

Prometheus depends on FastAPI and scrapes both FastAPI and postgres_exporter metrics.

Grafana depends on Prometheus and uses the provisioned Prometheus datasource.

---

## 8. Current Limitations

This monitoring setup is intentionally lightweight.

Current limitations:

- no Alertmanager routing
- no email, Slack, or PagerDuty notification
- no high-availability Prometheus setup
- no long-term metrics storage
- no production-grade authentication for Grafana
- no SLA/SLO error budget automation

These limitations are acceptable for the current Master thesis demonstrator and are clearly identified as future production improvements.

---

## 9. Production Improvement Path

For a production trajectory, the next steps would be:

1. Add Alertmanager for alert routing.
2. Define notification channels.
3. Add authentication and secret management.
4. Add long-term metrics storage.
5. Define SLOs and error budgets.
6. Add infrastructure-level metrics.
7. Add container image vulnerability scanning.
8. Add dashboard review and alert tuning process.

---

## 10. Oral Defense Positioning

During the defense, this monitoring setup can be presented as follows:

```text
RetailFlow includes an observability layer based on Prometheus, Grafana, and postgres_exporter.
Prometheus scrapes FastAPI and PostgreSQL exporter metrics, evaluates platform alerting rules,
and exposes target and rule status through its API.

Grafana provides visual dashboards for platform monitoring. Alerting rules are versioned in the repository
and loaded automatically through Docker Compose.

For the demonstrator, alerts are evaluated but not routed to external notification channels.
This keeps the platform realistic and verifiable while avoiding unnecessary production complexity.
```
