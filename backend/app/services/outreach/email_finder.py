"""
Finds professional email addresses via Hunter.io API.
Falls back to common pattern guessing.
"""
import httpx
import re
from ...config import settings


async def find_email(company_domain: str, first_name: str = "", last_name: str = "") -> dict:
    if settings.hunter_api_key and first_name and last_name:
        return await _hunter_find(company_domain, first_name, last_name)
    if company_domain:
        return await _guess_pattern(company_domain, first_name, last_name)
    return {"email": None, "confidence": 0}


async def _hunter_find(domain: str, first_name: str, last_name: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                "https://api.hunter.io/v2/email-finder",
                params={
                    "domain": domain,
                    "first_name": first_name,
                    "last_name": last_name,
                    "api_key": settings.hunter_api_key,
                },
            )
            data = res.json().get("data", {})
            return {
                "email": data.get("email"),
                "confidence": data.get("score", 0),
                "source": "hunter",
            }
    except Exception:
        return {"email": None, "confidence": 0}


async def _guess_pattern(domain: str, first_name: str, last_name: str) -> dict:
    if not first_name or not last_name:
        return {"email": None, "confidence": 0}

    fn = first_name.lower()
    ln = last_name.lower()
    patterns = [
        f"{fn}.{ln}@{domain}",
        f"{fn}@{domain}",
        f"{fn[0]}{ln}@{domain}",
        f"{fn}{ln[0]}@{domain}",
    ]
    return {
        "email": patterns[0],
        "email_patterns": patterns,
        "confidence": 25,
        "source": "pattern_guess",
        "note": "Unverified pattern. Add Hunter.io API key for verified emails.",
    }


def extract_domain_from_url(url: str) -> str:
    match = re.search(r"(?:https?://)?(?:www\.)?([^/\s]+\.[a-z]{2,})", url or "")
    return match.group(1) if match else ""
