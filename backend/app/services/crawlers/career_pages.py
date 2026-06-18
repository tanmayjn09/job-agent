"""
Scrapes company career pages via public ATS APIs.
Greenhouse and Lever both expose unauthenticated JSON endpoints
for their job boards — this covers hundreds of companies.
"""
import httpx
from .base import BaseCrawler, normalize_job

GREENHOUSE_COMPANIES = [
    "airbnb", "stripe", "notion", "figma", "airtable", "asana",
    "brex", "plaid", "robinhood", "coinbase", "databricks",
    "scale-ai", "openai", "anthropic", "hubspot", "zendesk",
]

LEVER_COMPANIES = [
    "netflix", "shopify", "atlassian", "canva", "linear",
    "vercel", "cloudflare", "datadog", "hashicorp", "postman",
    "segment", "mixpanel", "amplitude", "retool", "rippling",
]


class CareerPagesCrawler(BaseCrawler):
    source_name = "career_pages"

    async def search(self, query: str, location: str = "", **kwargs) -> list[dict]:
        query_terms = query.lower().split()
        jobs = []

        async with httpx.AsyncClient(timeout=15) as client:
            for company in GREENHOUSE_COMPANIES:
                try:
                    res = await client.get(
                        f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs",
                        params={"content": "true"},
                    )
                    if res.status_code != 200:
                        continue
                    data = res.json()
                    for job in data.get("jobs", []):
                        title = job.get("title", "")
                        if not any(t in title.lower() for t in query_terms):
                            continue
                        loc = job.get("location", {}).get("name", location)
                        jobs.append(normalize_job(
                            title=title,
                            company=company.replace("-", " ").title(),
                            location=loc,
                            description=job.get("content", "")[:3000],
                            url=job.get("absolute_url", ""),
                            source=self.source_name,
                            posted_at=job.get("updated_at", ""),
                            remote="remote" in loc.lower(),
                        ))
                except Exception:
                    continue

            for company in LEVER_COMPANIES:
                try:
                    res = await client.get(
                        f"https://api.lever.co/v0/postings/{company}",
                        params={"mode": "json"},
                    )
                    if res.status_code != 200:
                        continue
                    for job in res.json():
                        title = job.get("text", "")
                        if not any(t in title.lower() for t in query_terms):
                            continue
                        loc = job.get("categories", {}).get("location", location)
                        commitment = job.get("categories", {}).get("commitment", "")
                        jobs.append(normalize_job(
                            title=title,
                            company=company.title(),
                            location=loc,
                            description=job.get("descriptionPlain", "")[:3000],
                            url=job.get("hostedUrl", ""),
                            source=self.source_name,
                            posted_at=str(job.get("createdAt", "")),
                            employment_type=commitment,
                            remote="remote" in loc.lower(),
                        ))
                except Exception:
                    continue

        return jobs
