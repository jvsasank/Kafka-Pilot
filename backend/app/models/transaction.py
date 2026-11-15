from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import CheckConstraint, Index
from app.models import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    event_id = db.Column(db.String(128), unique=True, nullable=False, index=True)
    account_id = db.Column(db.String(80), nullable=False, index=True)
    merchant = db.Column(db.String(160), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="USD")
    country = db.Column(db.String(2), nullable=False, default="US")
    channel = db.Column(db.String(32), nullable=False, default="card")
    status = db.Column(db.String(32), nullable=False, default="authorized")
    risk_score = db.Column(db.Integer, nullable=False, default=0)
    risk_level = db.Column(db.String(16), nullable=False, default="low")
    reasons = db.Column(db.JSON, nullable=False, default=list)
    raw_event = db.Column(db.JSON, nullable=False, default=dict)
    occurred_at = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="risk_score_range"),
        Index("ix_transactions_created_risk", "created_at", "risk_level"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_id": self.event_id,
            "account_id": self.account_id,
            "merchant": self.merchant,
            "amount": float(self.amount),
            "currency": self.currency,
            "country": self.country,
            "channel": self.channel,
            "status": self.status,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "reasons": self.reasons,
            "occurred_at": self.occurred_at.isoformat(),
            "created_at": self.created_at.isoformat(),
        }
