from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "kafka-pilot-api"
    env: str = "development"
    database_url: str = "postgresql+psycopg://kafka:kafka@postgres:5432/kafka_pilot"
    cors_origins: str = "*"
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic: str = "financial-transactions"
    kafka_group_id: str = "kafka-pilot-consumer"
    alert_webhook_url: str | None = None
    high_risk_threshold: int = 75
    critical_risk_threshold: int = 90

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
