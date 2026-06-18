import httpx
from .base import BaseCrawler, normalize_job


class NaukriCrawler(BaseCrawler):
    source_name = "naukri"

    async def search(self, query: str, location: str = "", **kwargs) -> list[dict]:
        headers = {
            "appid": "109",
            "systemid": "109",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        }
        params = {
            "noOfResults": 20,
            "urlType": "search_by_key_loc",
            "searchType": "adv",
            "keyword": query,
            "location": location or "india",
            "pageNo": 1,
            "sort": "r",
            "experience": 0,
        }
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                res = await client.get(
                    "https://www.naukri.com/jobapi/v3/search",
                    params=params,
                    headers=headers,
                )
                data = res.json()
        except Exception:
            return []

        jobs = []
        for item in data.get("jobDetails", []):
            title = item.get("title", "")
            company = item.get("companyName", "")
            loc = ", ".join(item.get("placeholders", [{}])[0].get("label", "").split(",")[:2]) if item.get("placeholders") else location
            url = item.get("jdURL", "") or f"https://www.naukri.com{item.get('staticUrl', '')}"
            desc_parts = [p.get("label", "") for p in item.get("placeholders", [])]
            description = " | ".join(desc_parts)
            posted_at = item.get("footerPlaceholderLabel", "")
            salary_label = next((p.get("label", "") for p in item.get("placeholders", []) if p.get("type") == "salary"), "")

            jobs.append(normalize_job(
                title=title,
                company=company,
                location=loc or location,
                description=description,
                url=url,
                source=self.source_name,
                posted_at=posted_at,
                remote="remote" in loc.lower() or "work from home" in desc_parts[0].lower() if desc_parts else False,
            ))
        return jobs
