"""
Funding signals via Crunchbase API.
Falls back to scraping TechCrunch funding news if no API key.
"""
import httpx
from datetime import datetime, timedelta
from ...config import settings


async def get_funding_signal(company_name: str) -> dict:
    """Returns recent funding data for a company."""
    if settings.crunchbase_api_key:
        return await _fetch_crunchbase(company_name)
    return await _scrape_funding_news(company_name)


async def _fetch_crunchbase(company_name: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                "https://api.crunchbase.com/api/v4/entities/organizations",
                params={
                    "user_key": settings.crunchbase_api_key,
                    "field_ids": "short_description,last_funding_type,last_funding_total,founded_on,num_employees_enum",
                    "query": company_name,
                },
            )
            data = res.json()
            entities = data.get("entities", [])
            if not entities:
                return {}
            org = entities[0].get("properties", {})
            return {
                "last_funding_type": org.get("last_funding_type", ""),
                "last_funding_total": org.get("last_funding_total", {}).get("value_usd", 0),
                "employee_count": org.get("num_employees_enum", ""),
                "description": org.get("short_description", ""),
                "signal_score": _funding_score(org.get("last_funding_type", "")),
            }
    except Exception:
        return {}


async def _scrape_funding_news(company_name: str) -> dict:
    """Google News search for recent funding - no API key needed."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                "https://news.google.com/rss/search",
                params={"q": f"{company_name} funding raised series", "hl": "en-US"},
                headers={"User-Agent": "Mozilla/5.0"},
            )
        import xml.etree.ElementTree as ET
        root = ET.fromstring(res.text)
        channel = root.find("channel")
        items = channel.findall("item") if channel else []
        if not items:
            return {}
        latest = items[0]
        title = latest.findtext("title", "")
        pub_date = latest.findtext("pubDate", "")
        link = latest.findtext("link", "")
        has_recent_funding = any(kw in title.lower() for kw in ["raises", "raised", "series", "funding", "million", "billion"])
        return {
            "latest_news": title,
            "news_date": pub_date,
            "news_url": link,
            "has_recent_funding": has_recent_funding,
            "signal_score": 80 if has_recent_funding else 20,
        }
    except Exception:
        return {}


def _funding_score(funding_type: str) -> int:
    scores = {
        "seed": 60, "angel": 50, "series_a": 75, "series_b": 85,
        "series_c": 80, "series_d": 75, "ipo": 70, "grant": 40,
    }
    return scores.get(funding_type.lower().replace(" ", "_"), 30)
