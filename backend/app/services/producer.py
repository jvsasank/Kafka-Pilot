import json
import random
import time
from datetime import datetime, timezone

from confluent_kafka import Producer

from app.core.config import settings

MERCHANTS = [
    "Neighborhood Market",
    "Atlas Crypto Desk",
    "Northstar Gift Cards",
    "Bluebird Travel",
    "Metro Utilities",
    "Stadium Betting",
]


def build_event(index: int) -> dict:
    risky = random.random() > 0.58
    return {
        "event_id": f"evt-seed-{int(time.time())}-{index}",
        "account_id": f"acct-{random.randint(1, 25)}",
        "merchant": random.choice(MERCHANTS if risky else MERCHANTS[:1]),
        "amount": round(random.uniform(2500, 18000) if risky else random.uniform(7, 850), 2),
        "currency": "USD",
        "country": random.choice(["US", "US", "GB", "CA", "NG", "RU"] if risky else ["US", "CA"]),
        "channel": random.choice(["card", "manual_entry", "wire"] if risky else ["card"]),
        "account_velocity_10m": random.randint(4, 12) if risky else random.randint(0, 3),
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }


def run(count: int = 100) -> None:
    producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})
    for index in range(count):
        producer.produce(settings.kafka_topic, json.dumps(build_event(index)).encode("utf-8"))
        producer.poll(0)
    producer.flush()
    print(f"published {count} events to {settings.kafka_topic}")


if __name__ == "__main__":
    run()
