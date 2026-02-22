# backend/matchmaking.py

def calculate_match_score(exporter, buyer):
    score = 0

    # 1️⃣ Industry Match (30%)
    if exporter["industry"].lower() == buyer["industry"].lower():
        score += 30

    # 2️⃣ Risk Compatibility (20%)
    risk_weight = {
        "low": 20,
        "medium": 10,
        "high": 0
    }
    score += risk_weight.get(buyer["risk_level"].lower(), 0)

    # 3️⃣ Trade Volume Compatibility (20%)
    volume_diff = abs(exporter["trade_volume"] - buyer["trade_volume"])
    if volume_diff < 100000:
        score += 20
    elif volume_diff < 300000:
        score += 10

    # 4️⃣ Lead Score Compatibility (15%)
    if exporter["lead_score"] > 85:
        score += 15
    elif exporter["lead_score"] > 70:
        score += 8

    # 5️⃣ Historical Success (15%)
    score += buyer.get("success_rate", 5)

    return min(score, 100)


def generate_matches(exporter, buyers):
    results = []

    for buyer in buyers:
        buyer_copy = buyer.copy()
        buyer_copy["match_score"] = calculate_match_score(exporter, buyer)
        results.append(buyer_copy)

    return sorted(results, key=lambda x: x["match_score"], reverse=True)
