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


SERVICE_SIGNALS = {"agency", "digital media", "consulting", "staffing", "outsourcing", "bpo", "kpo", "recruitment", "manpower", "solutions pvt", "infotech", "infosys", "wipro", "tcs", "hcl", "cognizant", "accenture", "capgemini", "tech mahindra"}
PRODUCT_SIGNALS = {"saas", "platform", "software", "technologies", "labs", "ai", "cloud", "product", "startup", "inc.", "corp.", "ltd"}
SERVICE_EXCLUDE = {"agency", "digital media", "consulting", "staffing", "outsourcing", "bpo", "recruitment", "manpower"}
PRODUCT_EXCLUDE = SERVICE_SIGNALS


def filter_by_company_type(jobs: list[dict], company_type: str) -> list[dict]:
    if not company_type:
        return jobs

    def company_text(job):
        return (job.get("company", "") + " " + job.get("description", "")[:300]).lower()

    if company_type == "product":
        filtered = [j for j in jobs if not any(s in company_text(j) for s in SERVICE_EXCLUDE)]
        return filtered if filtered else jobs

    if company_type == "service":
        filtered = [j for j in jobs if any(s in company_text(j) for s in SERVICE_SIGNALS)]
        return filtered if filtered else jobs

    if company_type == "startup":
        filtered = [j for j in jobs if any(s in company_text(j) for s in {"startup", "seed", "series a", "early stage", "founded", "yc", "y combinator", "backed"})]
        return filtered if filtered else jobs

    return jobs


def filter_by_locations(jobs: list[dict], locations: list[str]) -> list[dict]:
    """Keep jobs that match requested locations or are remote. Falls back to all if nothing matches."""
    clean = [l.strip() for l in locations if l.strip()]
    if not clean:
        return jobs

    location_terms = set()
    for loc in clean:
        for word in loc.lower().split():
            if len(word) > 2:
                location_terms.add(word)

    matched, remote_only = [], []
    for job in jobs:
        job_loc = job.get("location", "").lower()
        is_remote = job.get("remote", False) or "remote" in job_loc or "anywhere" in job_loc
        loc_match = any(term in job_loc for term in location_terms)
        if loc_match:
            matched.append(job)
        elif is_remote:
            remote_only.append(job)

    return matched + remote_only if (matched or remote_only) else jobs


def prefilter_jobs(jobs: list[dict], query: str, locations: list[str] = None, limit: int = 60) -> list[dict]:
    """Keyword-score jobs against query and location. Returns top N."""
    query_terms = set(query.lower().split())
    stop = {"a", "an", "the", "in", "at", "for", "of", "and", "or", "to", "with"}
    query_terms -= stop

    location_terms = set()
    for loc in (locations or []):
        for word in loc.lower().split():
            if len(word) > 2:
                location_terms.add(word)

    def keyword_score(job: dict) -> int:
        text = (job.get("title", "") + " " + job.get("description", "")[:500]).lower()
        score = sum(1 for t in query_terms if t in text)
        if location_terms:
            job_loc = job.get("location", "").lower()
            if any(term in job_loc for term in location_terms):
                score += 5
        return score

    scored = sorted(jobs, key=keyword_score, reverse=True)
    return scored[:limit]


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

    unique = deduplicate_jobs(all_jobs)
    location_filtered = filter_by_locations(unique, locations)
    return prefilter_jobs(location_filtered, query, locations=locations, limit=60)


def apply_company_type_filter(jobs: list[dict], company_type: str) -> list[dict]:
    return filter_by_company_type(jobs, company_type)
