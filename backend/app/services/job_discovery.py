import hashlib
import json
import asyncio
from typing import Optional
import httpx
from ..config import settings
from .crawlers.aggregator import crawl_all_sources


def _job_hash(title: str, company: str, location: str) -> str:
    key = f"{title.lower().strip()}-{company.lower().strip()}-{location.lower().strip()}"
    return hashlib.md5(key.encode()).hexdigest()


def search_jobs_serpapi(
    query: str,
    location: str = "",
    remote: Optional[bool] = None,
    date_posted: str = "month",
    employment_type: Optional[str] = None,
    num: int = 20,
) -> list[dict]:
    if not settings.serpapi_key:
        return []

    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": settings.serpapi_key,
        "num": num,
    }

    if location:
        params["location"] = location
    if date_posted:
        date_map = {"24h": "today", "week": "3days", "month": "month"}
        params["chips"] = f"date_posted:{date_map.get(date_posted, 'month')}"
    if employment_type:
        params["employment_type"] = employment_type.upper()
    if remote:
        params["q"] += " remote"

    try:
        response = httpx.get("https://serpapi.com/search", params=params, timeout=30)
        data = response.json()
        jobs = data.get("jobs_results", [])
        return [_normalize_serpapi_job(j) for j in jobs]
    except Exception:
        return []


def _normalize_serpapi_job(raw: dict) -> dict:
    extensions = raw.get("detected_extensions", {})
    return {
        "title": raw.get("title", ""),
        "company": raw.get("company_name", ""),
        "location": raw.get("location", ""),
        "description": raw.get("description", ""),
        "url": raw.get("share_link", raw.get("job_link", "")),
        "source": "google_jobs",
        "posted_at": extensions.get("posted_at", ""),
        "remote": "remote" in raw.get("location", "").lower() or extensions.get("work_from_home", False),
        "employment_type": extensions.get("schedule_type", ""),
        "salary_min": None,
        "salary_max": None,
        "_hash": _job_hash(raw.get("title", ""), raw.get("company_name", ""), raw.get("location", "")),
    }


def scrape_linkedin_jobs(query: str, location: str = "", num: int = 20) -> list[dict]:
    params = {
        "keywords": query,
        "location": location,
        "count": num,
        "start": 0,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
    try:
        response = httpx.get(
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search",
            params=params,
            headers=headers,
            timeout=20,
            follow_redirects=True,
        )
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = []
        for card in soup.find_all("li")[:num]:
            title_el = card.find("h3")
            company_el = card.find("h4")
            location_el = card.find("span", {"class": lambda c: c and "job-search-card__location" in c})
            link_el = card.find("a", href=True)
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            company = company_el.get_text(strip=True) if company_el else ""
            loc = location_el.get_text(strip=True) if location_el else location
            url = link_el["href"].split("?")[0] if link_el else ""
            jobs.append({
                "title": title,
                "company": company,
                "location": loc,
                "description": "",
                "url": url,
                "source": "linkedin",
                "posted_at": "",
                "remote": "remote" in loc.lower(),
                "employment_type": "",
                "salary_min": None,
                "salary_max": None,
                "_hash": _job_hash(title, company, loc),
            })
        return jobs
    except Exception:
        return []


def deduplicate_jobs(jobs: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for job in jobs:
        h = job.get("_hash", _job_hash(job.get("title", ""), job.get("company", ""), job.get("location", "")))
        if h not in seen:
            seen.add(h)
            unique.append(job)
    return unique


async def discover_jobs(
    query: str,
    locations: list[str] = None,
    remote: Optional[bool] = None,
    date_posted: str = "month",
    employment_type: Optional[str] = None,
    num_per_source: int = 15,
) -> list[dict]:
    locations = locations or [""]
    all_jobs = []

    # SerpAPI (Google Jobs) - primary source
    for location in locations[:3]:
        serpapi_jobs = search_jobs_serpapi(
            query=query,
            location=location,
            remote=remote,
            date_posted=date_posted,
            employment_type=employment_type,
            num=num_per_source,
        )
        all_jobs.extend(serpapi_jobs)

    # Multi-source crawlers - RemoteOK, WeWorkRemotely, HN, Wellfound, YC, Greenhouse/Lever career pages
    crawler_jobs = await crawl_all_sources(
        query=query,
        locations=locations,
        remote=remote,
    )
    all_jobs.extend(crawler_jobs)

    # LinkedIn fallback if no SerpAPI key
    if not settings.serpapi_key:
        for location in locations[:2]:
            linkedin_jobs = scrape_linkedin_jobs(query=query, location=location, num=num_per_source)
            all_jobs.extend(linkedin_jobs)

    return deduplicate_jobs(all_jobs)
