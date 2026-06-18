import httpx
from bs4 import BeautifulSoup
from .base import BaseCrawler, normalize_job


class IndeedCrawler(BaseCrawler):
    source_name = "indeed"

    async def search(self, query: str, location: str = "", **kwargs) -> list[dict]:
        # Use India domain if location looks Indian, else global
        indian_cities = {"bengaluru", "bangalore", "mumbai", "delhi", "hyderabad", "pune", "chennai", "kolkata", "noida", "gurugram", "india"}
        use_india = not location or any(city in location.lower() for city in indian_cities)
        base = "https://in.indeed.com" if use_india else "https://www.indeed.com"

        params = {"q": query, "l": location, "limit": 20, "fromage": 30}
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                res = await client.get(f"{base}/jobs", params=params, headers=headers)
                soup = BeautifulSoup(res.text, "html.parser")
        except Exception:
            return []

        jobs = []
        for card in soup.find_all("div", class_=lambda c: c and "job_seen_beacon" in c)[:20]:
            title_el = card.find("h2", class_=lambda c: c and "jobTitle" in c)
            company_el = card.find("span", {"data-testid": "company-name"})
            loc_el = card.find("div", {"data-testid": "text-location"})
            date_el = card.find("span", {"data-testid": "myJobsStateDate"}) or card.find("span", class_=lambda c: c and "date" in (c or ""))
            link_el = card.find("a", href=True)

            title = title_el.get_text(strip=True) if title_el else ""
            if not title:
                continue
            company = company_el.get_text(strip=True) if company_el else ""
            loc = loc_el.get_text(strip=True) if loc_el else location
            posted_at = date_el.get_text(strip=True) if date_el else ""
            href = link_el["href"] if link_el else ""
            url = f"{base}{href}" if href.startswith("/") else href

            jobs.append(normalize_job(
                title=title,
                company=company,
                location=loc,
                description="",
                url=url,
                source=self.source_name,
                posted_at=posted_at,
                remote="remote" in loc.lower(),
            ))
        return jobs
