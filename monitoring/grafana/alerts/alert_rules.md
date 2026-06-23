# RetailFlow Grafana Alert Rules

## 1. FastAPI Down

Query:
up{job="retailflow-fastapi"} == 0

Condition:
- IS ABOVE 0

Evaluation:
- every 15s
- for 1 minute

Meaning:
FastAPI API service is unreachable by Prometheus.

---

## 2. PostgreSQL Down

Query:
pg_up{job="retailflow-postgres"} == 0

Condition:
- IS ABOVE 0

Evaluation:
- every 15s
- for 1 minute

Meaning:
PostgreSQL exporter cannot reach the database.

---

## 3. High API Error Rate

Query:
sum(rate(http_requests_total{status=~"5.."}[1m]))

Condition:
- IS ABOVE 0

Evaluation:
- every 15s
- for 1 minute

Meaning:
The API is generating HTTP 5xx server errors.

---

## 4. High API Latency (p95)

Query:
histogram_quantile(
  0.95,
  sum by (le) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)

Condition:
- IS ABOVE 1

Evaluation:
- every 15s
- for 2 minutes

Meaning:
95th percentile API latency exceeds 1 second.

---

## 5. Drift Detected (conceptual alert)

Query:
vector(1)

Usage:
Manual/business alert placeholder.

Meaning:
Current ML drift detection is generated from JSON reports, not native Prometheus metrics yet.
This alert demonstrates how ML monitoring could trigger operational alerts.

