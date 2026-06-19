import asyncio
import httpx
from bs4 import BeautifulSoup
from .base import BaseCrawler, normalize_job


class LinkedInCrawler(BaseCrawler):
    source_name = "linkedin"

    async def search(self, query: str, location: str = "", **kwargs) -> list[dict]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        jobs = []
        async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as client:
            for start in [0, 25, 50]:
                params = {
                    "keywords": query,
                    "location": location or "India",
                    "start": start,
                    "count": 25,
                    "f_TPR": "r2592000",  # last 30 days
                }
                try:
                    res = await client.get(
                        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search",
                        params=params,
                    )
                    soup = BeautifulSoup(res.text, "html.parser")
                except Exception:
                    break

                cards = soup.find_all("li")
                if not cards:
                    break

                for card in cards:
                    title_el = card.find("h3", class_=lambda c: c and "base-search-card__title" in c)
                    company_el = card.find("h4", class_=lambda c: c and "base-search-card__subtitle" in c)
                    loc_el = card.find("span", class_=lambda c: c and "job-search-card__location" in c)
                    date_el = card.find("time")
                    link_el = card.find("a", class_=lambda c: c and "base-card__full-link" in c)

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    company = company_el.get_text(strip=True) if company_el else ""
                    loc = loc_el.get_text(strip=True) if loc_el else location
                    posted_at = date_el.get("datetime", "") if date_el else ""
                    url = link_el["href"].split("?")[0] if link_el and link_el.get("href") else ""

                    jobs.append(normalize_job(
                        title=title,
                        company=company,
                        location=loc,
                        description="",  # fetched on-demand in resume tailor
                        url=url,
                        source=self.source_name,
                        posted_at=posted_at,
                        remote="remote" in loc.lower(),
                    ))

                if len(cards) < 25:
                    break

                await asyncio.sleep(0.5)

        return jobs[:60]
