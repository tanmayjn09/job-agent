import re
import httpx
from bs4 import BeautifulSoup
from .base import BaseCrawler, normalize_job


class LinkedInCrawler(BaseCrawler):
    source_name = "linkedin"

    async def _fetch_description(self, client: httpx.AsyncClient, job_url: str) -> str:
        """Fetch job description from LinkedIn public job detail page."""
        try:
            job_id_match = re.search(r"/view/(\d+)", job_url)
            if not job_id_match:
                return ""
            job_id = job_id_match.group(1)
            res = await client.get(
                f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}",
                timeout=10,
            )
            soup = BeautifulSoup(res.text, "html.parser")
            desc_el = soup.find("div", class_=lambda c: c and "description__text" in c)
            if desc_el:
                return desc_el.get_text(separator="\n", strip=True)[:3000]
        except Exception:
            pass
        return ""

    async def search(self, query: str, location: str = "", **kwargs) -> list[dict]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        jobs = []
        async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as client:
            for start in [0, 25]:
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

                    description = await self._fetch_description(client, url)

                    jobs.append(normalize_job(
                        title=title,
                        company=company,
                        location=loc,
                        description=description,
                        url=url,
                        source=self.source_name,
                        posted_at=posted_at,
                        remote="remote" in loc.lower(),
                    ))

                if len(cards) < 25:
                    break

        return jobs[:40]
