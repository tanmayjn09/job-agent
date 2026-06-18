"""
Scores a job based on post age.
Apply within 48h for 3x better response rate.
"""
from datetime import datetime, timezone
import re


def parse_post_age_hours(posted_at: str) -> float | None:
    if not posted_at:
        return None

    posted_at = posted_at.strip()

    relative_patterns = [
        (r"(\d+)\s*hour", lambda m: float(m.group(1))),
        (r"(\d+)\s*day", lambda m: float(m.group(1)) * 24),
        (r"(\d+)\s*week", lambda m: float(m.group(1)) * 24 * 7),
        (r"(\d+)\s*month", lambda m: float(m.group(1)) * 24 * 30),
        (r"just now|moments ago", lambda m: 0.5),
        (r"today", lambda m: 12.0),
        (r"yesterday", lambda m: 36.0),
    ]
    for pattern, calc in relative_patterns:
        m = re.search(pattern, posted_at.lower())
        if m:
            return calc(m)

    for fmt in [
        "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z", "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%d",
    ]:
        try:
            dt = datetime.strptime(posted_at, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            delta = now - dt
            return delta.total_seconds() / 3600
        except ValueError:
            continue

    return None


def score_post_age(posted_at: str) -> dict:
    age_hours = parse_post_age_hours(posted_at)

    if age_hours is None:
        return {"age_hours": None, "age_label": "unknown", "urgency_score": 50, "apply_now": False}

    if age_hours <= 24:
        label, score, urgent = "posted today", 100, True
    elif age_hours <= 48:
        label, score, urgent = "posted yesterday", 90, True
    elif age_hours <= 72:
        label, score, urgent = "2-3 days ago", 75, True
    elif age_hours <= 168:
        label, score, urgent = "this week", 60, False
    elif age_hours <= 720:
        label, score, urgent = "this month", 35, False
    else:
        label, score, urgent = "older", 15, False

    return {
        "age_hours": round(age_hours, 1),
        "age_label": label,
        "urgency_score": score,
        "apply_now": urgent,
    }
