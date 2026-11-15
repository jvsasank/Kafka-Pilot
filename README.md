# Kafka Pilot


Kafka Pilot is a production-oriented fraud monitoring platform for financial transaction streams. It uses React, Flask, PostgreSQL, Kafka, Docker, and ELK-style logging to ingest events, score risk, surface alerts, and give analysts a live operational dashboard.

## What is included

- Real-time Kafka consumer for `financial-transactions` events.
- Flask API with health checks, Prometheus metrics, structured JSON logs, transaction ingestion, risk summaries, and alert acknowledgment.
- PostgreSQL persistence with indexed transaction and alert models.
- React dashboard with KPI cards, risk distribution chart, alert queue, filters, and a sample event simulator.
- Docker Compose environment for Postgres, Kafka, backend API, consumer, frontend, Elasticsearch, Logstash, and Kibana.
- Focused backend tests for fraud scoring, alert creation, and dashboard summaries.

## Run locally

```bash
docker compose up --build
```

Open:

- Dashboard: http://localhost:3000
- API health: http://localhost:8000/healthz
- API metrics: http://localhost:8000/metrics
- Kibana: http://localhost:5601

Seed Kafka events:

```bash
docker compose run --rm backend python -m app.services.producer
```

You can also use the dashboard's **Simulate Event** button to POST a sample transaction directly through the API.

## API shape

Create or replay a transaction:

```bash
curl -X POST http://localhost:8000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt-1001",
    "account_id": "acct-42",
    "merchant": "Atlas Crypto Desk",
    "amount": "12500.00",
    "currency": "USD",
    "country": "NG",
    "channel": "wire",
    "account_velocity_10m": 9,
    "occurred_at": "2026-08-11T15:00:00Z"
  }'
```

Read operational data:

```bash
curl http://localhost:8000/api/summary
curl http://localhost:8000/api/transactions
curl http://localhost:8000/api/alerts
```

## Production notes

- Images are multi-stage or slim-runtime oriented to keep runtime footprint low.
- Gunicorn runs the Flask app with multiple workers.
- Kafka consumers manually commit offsets only after successful database ingestion.
- Event IDs are idempotent at the API/database layer.
- Structured JSON logs can be shipped into Logstash/Elasticsearch or any log collector.
- `/metrics` exposes Prometheus-compatible request metrics.
- Secrets should be supplied through a secrets manager or deployment environment, not committed `.env` files.

## Event contract

Required fields:

- `event_id`
- `account_id`
- `merchant`
- `amount`

Optional fields:

- `currency`
- `country`
- `channel`
- `status`
- `account_velocity_10m`
- `occurred_at`

Risk scoring combines amount, country, merchant category, channel, and short-window velocity. Transactions scoring at least `HIGH_RISK_THRESHOLD` create analyst alerts.
