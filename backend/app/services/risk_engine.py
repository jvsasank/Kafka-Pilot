from decimal import Decimal


HIGH_RISK_COUNTRIES = {"NG", "RU", "KP", "IR"}
SENSITIVE_MERCHANT_TERMS = {"crypto", "gift card", "wire", "betting", "atm"}


def score_transaction(event: dict) -> tuple[int, str, list[str]]:
    score = 5
    reasons: list[str] = []
    amount = Decimal(str(event.get("amount", 0)))
    merchant = str(event.get("merchant", "")).lower()
    country = str(event.get("country", "US")).upper()
    channel = str(event.get("channel", "card")).lower()

    if amount >= Decimal("10000"):
        score += 45
        reasons.append("large transaction amount")
    elif amount >= Decimal("2500"):
        score += 25
        reasons.append("elevated transaction amount")

    if country in HIGH_RISK_COUNTRIES:
        score += 25
        reasons.append("high-risk transaction country")

    if any(term in merchant for term in SENSITIVE_MERCHANT_TERMS):
        score += 20
        reasons.append("sensitive merchant category")

    if channel in {"manual_entry", "wire", "crypto"}:
        score += 15
        reasons.append("higher-risk payment channel")

    velocity = int(event.get("account_velocity_10m", 0) or 0)
    if velocity >= 8:
        score += 25
        reasons.append("rapid account transaction velocity")
    elif velocity >= 4:
        score += 12
        reasons.append("unusual account transaction velocity")

    score = min(score, 100)
    if score >= 90:
        level = "critical"
    elif score >= 75:
        level = "high"
    elif score >= 40:
        level = "medium"
    else:
        level = "low"

    if not reasons:
        reasons.append("baseline authorization risk")

    return score, level, reasons
