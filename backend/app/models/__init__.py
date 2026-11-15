from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.alert import Alert  # noqa: E402,F401
from app.models.transaction import Transaction  # noqa: E402,F401
