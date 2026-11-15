def test_high_risk_transaction_creates_alert(client):
    response = client.post(
        "/api/transactions",
        json={
            "event_id": "evt-test-1",
            "account_id": "acct-9",
            "merchant": "Atlas Crypto Desk",
            "amount": "12500.00",
            "country": "NG",
            "channel": "wire",
            "account_velocity_10m": 9,
            "occurred_at": "2026-08-11T15:00:00Z",
        },
    )

    assert response.status_code == 201
    assert response.json["risk_level"] == "critical"
    assert response.json["risk_score"] == 100

    alerts = client.get("/api/alerts").json
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "critical"


def test_summary_reports_volume(client):
    client.post(
        "/api/transactions",
        json={
            "event_id": "evt-test-2",
            "account_id": "acct-1",
            "merchant": "Local Market",
            "amount": "42.10",
        },
    )

    summary = client.get("/api/summary").json
    assert summary["total_transactions"] == 1
    assert summary["processed_volume"] == 42.1
