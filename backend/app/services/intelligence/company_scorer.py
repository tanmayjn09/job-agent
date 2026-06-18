"""
Combines all signals into a final priority score for a job.

priority_score = weighted combination of:
  - match_score (40%) - how well candidate fits
  - urgency_score (25%) - post age / apply fast
  - company_health (20%) - glassdoor + layoffs
  - funding_signal (15%) - recent funding = hiring mode
"""


def compute_priority_score(
    match_score: float,
    urgency_score: int,
    health_score: int,
    funding_score: int,
    competition_score: int,
) -> dict:
    priority = (
        match_score * 0.40 +
        urgency_score * 0.25 +
        health_score * 0.20 +
        funding_score * 0.15
    )

    if competition_score < 30:
        priority = priority * 0.85

    priority = max(0, min(100, priority))

    if priority >= 80:
        tier = "S"
        label = "Apply immediately"
    elif priority >= 65:
        tier = "A"
        label = "Strong opportunity"
    elif priority >= 50:
        tier = "B"
        label = "Worth applying"
    elif priority >= 35:
        tier = "C"
        label = "Lower priority"
    else:
        tier = "D"
        label = "Skip or apply last"

    return {
        "priority_score": round(priority, 1),
        "tier": tier,
        "label": label,
        "breakdown": {
            "match": round(match_score * 0.40, 1),
            "urgency": round(urgency_score * 0.25, 1),
            "health": round(health_score * 0.20, 1),
            "funding": round(funding_score * 0.15, 1),
        }
    }
