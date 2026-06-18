import httpx
from bs4 import BeautifulSoup
from .base import BaseCrawler, normalize_job


class YCJobsCrawler(BaseCrawler):
    """Scrapes Y Combinator job board."""
    source_name = "ycombinator"

    async def search(self, query: str, location: str = "", **kwargs) -> list[dict]:
        headers = {"User-Agent": "Mozilla/5.0"}
        query_terms = query.lower().split()

        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                res = await client.get("https://www.ycombinator.com/jobs", headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            jobs = []

            for card in soup.find_all("a", class_=lambda c: c and "job" in c.lower())[:50]:
                title_el = card.find(["h3", "h4", "strong"])
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                if not any(t in title.lower() for t in query_terms):
                    continue
                company_el = card.find("span", class_=lambda c: c and "company" in (c or "").lower())
                company = company_el.get_text(strip=True) if company_el else "YC Company"
                loc_el = card.find("span", class_=lambda c: c and "location" in (c or "").lower())
                loc = loc_el.get_text(strip=True) if loc_el else "Remote / US"
                href = card.get("href", "")
                url = f"https://www.ycombinator.com{href}" if href.startswith("/") else href

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

        return jobs[:15]
