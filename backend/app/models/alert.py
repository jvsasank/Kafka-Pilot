from datetime import datetime, timezone
from uuid import uuid4

from app.models import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    transaction_id = db.Column(db.String(36), db.ForeignKey("transactions.id"), nullable=False, index=True)
    severity = db.Column(db.String(16), nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    acknowledged = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    transaction = db.relationship("Transaction", backref=db.backref("alerts", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "acknowledged": self.acknowledged,
            "created_at": self.created_at.isoformat(),
            "transaction": self.transaction.to_dict() if self.transaction else None,
        }
