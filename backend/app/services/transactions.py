from datetime import datetime, timezone
from decimal import Decimal

import structlog
from sqlalchemy import func

from app.core.config import settings
from app.models import db
from app.models.alert import Alert
from app.models.transaction import Transaction
from app.services.risk_engine import score_transaction

logger = structlog.get_logger()


def parse_event_time(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def ingest_transaction(event: dict) -> Transaction:
    score, level, reasons = score_transaction(event)
    transaction = Transaction(
        event_id=str(event["event_id"]),
        account_id=str(event["account_id"]),
        merchant=str(event["merchant"]),
        amount=Decimal(str(event["amount"])),
        currency=str(event.get("currency", "USD")),
        country=str(event.get("country", "US")),
        channel=str(event.get("channel", "card")),
        status=str(event.get("status", "authorized")),
        risk_score=score,
        risk_level=level,
        reasons=reasons,
        raw_event=event,
        occurred_at=parse_event_time(event.get("occurred_at")),
    )
    db.session.add(transaction)
    db.session.flush()

    if score >= settings.high_risk_threshold:
        severity = "critical" if score >= settings.critical_risk_threshold else "high"
        alert = Alert(
            transaction_id=transaction.id,
            severity=severity,
            title=f"{severity.title()} fraud risk detected",
            description=", ".join(reasons),
        )
        db.session.add(alert)
        logger.warning("fraud_alert_created", transaction_id=str(transaction.id), risk_score=score, severity=severity)

    db.session.commit()
    logger.info("transaction_ingested", event_id=transaction.event_id, risk_level=level, risk_score=score)
    return transaction


def dashboard_summary() -> dict:
    total = db.session.scalar(db.select(func.count(Transaction.id))) or 0
    high_risk = db.session.scalar(
        db.select(func.count(Transaction.id)).where(Transaction.risk_level.in_(["high", "critical"]))
    ) or 0
    unacked_alerts = db.session.scalar(db.select(func.count(Alert.id)).where(Alert.acknowledged.is_(False))) or 0
    volume = db.session.scalar(db.select(func.coalesce(func.sum(Transaction.amount), 0))) or 0

    risk_rows = db.session.execute(
        db.select(Transaction.risk_level, func.count(Transaction.id)).group_by(Transaction.risk_level)
    ).all()

    return {
        "total_transactions": total,
        "high_risk_transactions": high_risk,
        "unacknowledged_alerts": unacked_alerts,
        "processed_volume": float(volume),
        "risk_distribution": {level: count for level, count in risk_rows},
    }
