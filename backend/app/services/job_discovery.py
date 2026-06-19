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


def search_jobs_jsearch(
    query: str,
    location: str = "",
    remote: Optional[bool] = None,
    date_posted: str = "month",
    num: int = 20,
) -> list[dict]:
    key = settings.rapidapi_key or settings.serpapi_key
    if not key or key in ("your_serpapi_key_here", "your_rapidapi_key_here"):
        return []

    q = query
    if location:
        q = f"{query} in {location}"
    if remote:
        q = f"{query} remote"

    date_map = {"24h": "today", "week": "week", "month": "month"}
    num_pages = max(1, min(num // 10, 5))

    params = {
        "query": q,
        "page": "1",
        "num_pages": str(num_pages),
        "date_posted": date_map.get(date_posted, "month"),
        "country": "in" if location and any(c in location.lower() for c in ["bengaluru", "bangalore", "mumbai", "delhi", "hyderabad", "pune", "india"]) else "us",
    }

    try:
        response = httpx.get(
            "https://jsearch.p.rapidapi.com/search",
            params=params,
            headers={
                "X-RapidAPI-Key": key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
            },
            timeout=30,
        )
        data = response.json()
        jobs = data.get("data", [])
        return [_normalize_jsearch_job(j) for j in jobs]
    except Exception:
        return []


def _normalize_jsearch_job(raw: dict) -> dict:
    loc_parts = [raw.get("job_city", ""), raw.get("job_state", ""), raw.get("job_country", "")]
    location = ", ".join(p for p in loc_parts if p)
    return {
        "title": raw.get("job_title", ""),
        "company": raw.get("employer_name", ""),
        "location": location,
        "description": raw.get("job_description", ""),
        "url": raw.get("job_apply_link", raw.get("job_google_link", "")),
        "source": "google_jobs",
        "posted_at": raw.get("job_posted_at_datetime_utc", raw.get("job_posted_at_timestamp", "")),
        "remote": raw.get("job_is_remote", False),
        "employment_type": raw.get("job_employment_type", ""),
        "salary_min": raw.get("job_min_salary"),
        "salary_max": raw.get("job_max_salary"),
        "_hash": _job_hash(raw.get("job_title", ""), raw.get("employer_name", ""), location),
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


def prefilter_jobs(jobs: list[dict], query: str, locations: list[str] = None, limit: int = 100) -> list[dict]:
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

    # JSearch / Google Jobs - all locations in parallel
    loop = asyncio.get_event_loop()
    jsearch_tasks = [
        loop.run_in_executor(None, search_jobs_jsearch, query, loc, remote, date_posted, num_per_source)
        for loc in locations[:3]
    ]
    jsearch_results = await asyncio.gather(*jsearch_tasks, return_exceptions=True)
    for r in jsearch_results:
        if not isinstance(r, Exception):
            all_jobs.extend(r)

    # Multi-source crawlers - RemoteOK, WeWorkRemotely, HN, Wellfound, YC, Greenhouse/Lever career pages
    crawler_jobs = await crawl_all_sources(
        query=query,
        locations=locations,
        remote=remote,
    )
    all_jobs.extend(crawler_jobs)

    # LinkedIn fallback if no Google Jobs key
    key = settings.rapidapi_key or settings.serpapi_key
    if not key or key in ("your_serpapi_key_here", "your_rapidapi_key_here"):
        for location in locations[:2]:
            linkedin_jobs = scrape_linkedin_jobs(query=query, location=location, num=num_per_source)
            all_jobs.extend(linkedin_jobs)

    unique = deduplicate_jobs(all_jobs)
    location_filtered = filter_by_locations(unique, locations)
    return prefilter_jobs(location_filtered, query, locations=locations, limit=120)


def apply_company_type_filter(jobs: list[dict], company_type: str) -> list[dict]:
    return filter_by_company_type(jobs, company_type)
