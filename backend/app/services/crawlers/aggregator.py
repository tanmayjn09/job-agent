import asyncio
from .base import job_hash
from .remoteok import RemoteOKCrawler
from .weworkremotely import WeWorkRemotelyCrawler
from .hn_jobs import HackerNewsJobsCrawler
from .wellfound import WellfoundCrawler
from .yc_jobs import YCJobsCrawler
from .career_pages import CareerPagesCrawler
from .naukri import NaukriCrawler
from .indeed import IndeedCrawler
from .remotive import RemotiveCrawler

ALL_CRAWLERS = [
    NaukriCrawler(),       # India's #1 job portal
    IndeedCrawler(),       # Global + India (in.indeed.com)
    RemotiveCrawler(),     # Remote jobs with public API
    RemoteOKCrawler(),
    WeWorkRemotelyCrawler(),
    WellfoundCrawler(),
    YCJobsCrawler(),
    HackerNewsJobsCrawler(),
    CareerPagesCrawler(),
]


async def crawl_all_sources(
    query: str,
    locations: list[str] = None,
    remote: bool = None,
    crawlers=None,
) -> list[dict]:
    locations = locations or [""]
    crawlers = crawlers or ALL_CRAWLERS
    location = locations[0] if locations else ""

    tasks = [crawler.search(query=query, location=location) for crawler in crawlers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_jobs = []
    for result in results:
        if isinstance(result, Exception):
            continue
        all_jobs.extend(result)

    if remote is True:
        all_jobs = [j for j in all_jobs if j.get("remote")]

    seen = set()
    unique = []
    for job in all_jobs:
        h = job.get("_hash") or job_hash(job.get("title", ""), job.get("company", ""), job.get("location", ""))
        if h not in seen:
            seen.add(h)
            unique.append(job)

    return unique
