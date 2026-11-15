from flask import Blueprint, jsonify, request

from app.models import db
from app.models.alert import Alert
from app.models.transaction import Transaction
from app.services.transactions import dashboard_summary, ingest_transaction

api_bp = Blueprint("api", __name__)


@api_bp.get("/summary")
def summary():
    return jsonify(dashboard_summary())


@api_bp.get("/transactions")
def list_transactions():
    limit = min(int(request.args.get("limit", 50)), 200)
    risk_level = request.args.get("risk_level")
    query = Transaction.query.order_by(Transaction.created_at.desc())
    if risk_level:
        query = query.filter(Transaction.risk_level == risk_level)
    return jsonify([tx.to_dict() for tx in query.limit(limit).all()])


@api_bp.post("/transactions")
def create_transaction():
    payload = request.get_json(force=True)
    required = {"event_id", "account_id", "merchant", "amount"}
    missing = sorted(required - payload.keys())
    if missing:
        return {"error": "missing required fields", "fields": missing}, 400
    existing = Transaction.query.filter_by(event_id=payload["event_id"]).first()
    if existing:
        return existing.to_dict(), 200
    transaction = ingest_transaction(payload)
    return transaction.to_dict(), 201


@api_bp.get("/alerts")
def list_alerts():
    limit = min(int(request.args.get("limit", 50)), 200)
    rows = Alert.query.order_by(Alert.created_at.desc()).limit(limit).all()
    return jsonify([alert.to_dict() for alert in rows])


@api_bp.patch("/alerts/<alert_id>/ack")
def acknowledge_alert(alert_id: str):
    alert = Alert.query.get_or_404(alert_id)
    alert.acknowledged = True
    db.session.commit()
    return alert.to_dict()
