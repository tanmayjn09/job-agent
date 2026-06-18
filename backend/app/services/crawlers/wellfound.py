import httpx
from bs4 import BeautifulSoup
from .base import BaseCrawler, normalize_job


class WellfoundCrawler(BaseCrawler):
    """Scrapes AngelList/Wellfound startup jobs."""
    source_name = "wellfound"

    async def search(self, query: str, location: str = "", **kwargs) -> list[dict]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }
        params = {"q": query}
        if location:
            params["location"] = location

        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                res = await client.get(
                    "https://wellfound.com/jobs",
                    params=params,
                    headers=headers,
                )
            soup = BeautifulSoup(res.text, "html.parser")
            jobs = []

            for card in soup.find_all("div", attrs={"data-test": "StartupResult"})[:20]:
                title_el = card.find("a", attrs={"data-test": "job-title"})
                company_el = card.find("a", attrs={"data-test": "startup-link"})
                location_el = card.find("span", attrs={"data-test": "location"})
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                company = company_el.get_text(strip=True) if company_el else ""
                loc = location_el.get_text(strip=True) if location_el else location
                url = f"https://wellfound.com{title_el.get('href', '')}"
                jobs.append(normalize_job(
                    title=title,
                    company=company,
                    location=loc,
                    description="",
                    url=url,
                    source=self.source_name,
                    remote="remote" in loc.lower(),
                ))
        except Exception:
            return []

        return jobs
