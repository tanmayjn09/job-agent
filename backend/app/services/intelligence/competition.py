"""
Estimates competition level for a job.
Uses post age as a proxy - older posts have more applicants.
LinkedIn applicant counts scraped when available.
"""
import httpx
import re
from .post_scorer import parse_post_age_hours


def estimate_competition(posted_at: str, source: str = "") -> dict:
    """Heuristic competition estimate based on age and source."""
    age_hours = parse_post_age_hours(posted_at)

    if age_hours is None:
        return {"level": "unknown", "score": 50, "applicant_estimate": "Unknown"}

    if age_hours <= 24:
        level, score, estimate = "very_low", 95, "< 50 applicants"
    elif age_hours <= 48:
        level, score, estimate = "low", 80, "50-150 applicants"
    elif age_hours <= 72:
        level, score, estimate = "medium", 65, "150-300 applicants"
    elif age_hours <= 168:
        level, score, estimate = "medium", 50, "300-500 applicants"
    elif age_hours <= 336:
        level, score, estimate = "high", 30, "500-1000 applicants"
    else:
        level, score, estimate = "very_high", 10, "1000+ applicants"

    if source in ["career_pages", "ycombinator", "hackernews"]:
        score = min(100, score + 15)
        level = level.replace("high", "medium") if "high" in level else level

    return {
        "level": level,
        "score": score,
        "applicant_estimate": estimate,
    }


async def scrape_linkedin_applicant_count(job_url: str) -> int | None:
    """Try to get actual applicant count from LinkedIn job page."""
    if "linkedin.com" not in job_url:
        return None
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            res = await client.get(job_url, headers={"User-Agent": "Mozilla/5.0"})
        match = re.search(r"([\d,]+)\s+applicants?", res.text, re.IGNORECASE)
        if match:
            return int(match.group(1).replace(",", ""))
    except Exception:
        pass
    return None
