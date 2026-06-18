"""
Tracks how fast a company is posting jobs.
High velocity = active hiring spree = good time to apply.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...models.job import Job


def get_company_velocity(db: Session, company_name: str) -> dict:
    """Score a company's hiring velocity based on recent job postings in our DB."""
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    total_jobs = db.query(func.count(Job.id)).filter(
        Job.company.ilike(f"%{company_name}%")
    ).scalar() or 0

    recent_jobs = db.query(func.count(Job.id)).filter(
        Job.company.ilike(f"%{company_name}%"),
        Job.fetched_at >= week_ago,
    ).scalar() or 0

    month_jobs = db.query(func.count(Job.id)).filter(
        Job.company.ilike(f"%{company_name}%"),
        Job.fetched_at >= month_ago,
    ).scalar() or 0

    if month_jobs >= 10:
        velocity = "very_high"
        score = 95
    elif month_jobs >= 5:
        velocity = "high"
        score = 80
    elif month_jobs >= 2:
        velocity = "medium"
        score = 60
    elif month_jobs >= 1:
        velocity = "low"
        score = 40
    else:
        velocity = "unknown"
        score = 30

    return {
        "total_jobs_seen": total_jobs,
        "jobs_last_7_days": recent_jobs,
        "jobs_last_30_days": month_jobs,
        "velocity": velocity,
        "velocity_score": score,
    }
