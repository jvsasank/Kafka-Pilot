from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from prometheus_flask_exporter import PrometheusMetrics

from app.api.routes import api_bp
from app.core.config import settings
from app.core.logging import configure_logging
from app.models import db

migrate = Migrate()


def create_app(test_config: dict | None = None) -> Flask:
    configure_logging()
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.update(test_config or {})

    CORS(app, resources={r"/api/*": {"origins": settings.cors_origins}})
    db.init_app(app)
    migrate.init_app(app, db)
    PrometheusMetrics(app, group_by="endpoint")

    app.register_blueprint(api_bp, url_prefix="/api")

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("database tables ensured")

    @app.get("/healthz")
    def healthz():
        return {"status": "ok", "service": settings.app_name}

    return app
