"""
Company health signals: Glassdoor rating + layoffs check.
"""
import httpx
import json
from bs4 import BeautifulSoup


async def get_glassdoor_rating(company_name: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html",
    }
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            res = await client.get(
                "https://www.glassdoor.com/Search/results.htm",
                params={"keyword": company_name},
                headers=headers,
            )
        soup = BeautifulSoup(res.text, "html.parser")
        rating_el = soup.find("span", class_=lambda c: c and "rating" in (c or "").lower())
        if rating_el:
            try:
                rating = float(rating_el.get_text(strip=True))
                return {
                    "rating": rating,
                    "health_score": _rating_to_score(rating),
                    "source": "glassdoor",
                }
            except ValueError:
                pass
    except Exception:
        pass
    return {"rating": None, "health_score": 50, "source": "unknown"}


async def check_layoffs(company_name: str) -> dict:
    """Check Layoffs.fyi for recent layoffs."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                "https://layoffs.fyi/",
                headers={"User-Agent": "Mozilla/5.0"},
            )
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")
        if not table:
            return {"recent_layoffs": False, "layoff_score": 80}
        rows = table.find_all("tr")[1:20]
        for row in rows:
            cells = row.find_all("td")
            if cells and company_name.lower() in cells[0].get_text(strip=True).lower():
                return {
                    "recent_layoffs": True,
                    "layoff_score": 10,
                    "layoff_details": " | ".join(c.get_text(strip=True) for c in cells[:4]),
                }
    except Exception:
        pass
    return {"recent_layoffs": False, "layoff_score": 80}


def _rating_to_score(rating: float) -> int:
    if rating >= 4.0:
        return 90
    elif rating >= 3.5:
        return 75
    elif rating >= 3.0:
        return 55
    elif rating >= 2.5:
        return 35
    return 15


async def get_company_health(company_name: str) -> dict:
    glassdoor = await get_glassdoor_rating(company_name)
    layoffs = await check_layoffs(company_name)

    combined_score = int((glassdoor["health_score"] * 0.6) + (layoffs["layoff_score"] * 0.4))

    return {
        "glassdoor_rating": glassdoor.get("rating"),
        "recent_layoffs": layoffs["recent_layoffs"],
        "layoff_details": layoffs.get("layoff_details", ""),
        "health_score": combined_score,
        "health_label": _score_label(combined_score),
    }


def _score_label(score: int) -> str:
    if score >= 75:
        return "healthy"
    elif score >= 50:
        return "neutral"
    elif score >= 25:
        return "concerning"
    return "avoid"
