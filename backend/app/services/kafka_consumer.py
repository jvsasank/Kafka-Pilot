import json
import signal

import structlog
from confluent_kafka import Consumer, KafkaError

from app import create_app
from app.core.config import settings
from app.services.transactions import ingest_transaction

logger = structlog.get_logger()
running = True


def shutdown(*_args):
    global running
    running = False


def run_consumer() -> None:
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    consumer = Consumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": settings.kafka_group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([settings.kafka_topic])
    app = create_app()

    with app.app_context():
        while running:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    logger.error("kafka_consumer_error", error=str(msg.error()))
                continue

            try:
                event = json.loads(msg.value().decode("utf-8"))
                ingest_transaction(event)
                consumer.commit(msg)
            except Exception as exc:
                logger.exception("transaction_ingest_failed", error=str(exc))

    consumer.close()


if __name__ == "__main__":
    run_consumer()
