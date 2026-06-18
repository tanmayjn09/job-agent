import httpx
from .base import BaseCrawler, normalize_job


class RemoteOKCrawler(BaseCrawler):
    source_name = "remoteok"

    async def search(self, query: str, location: str = "", **kwargs) -> list[dict]:
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                res = await client.get("https://remoteok.com/api", headers=headers)
                data = res.json()
        except Exception:
            return []

        jobs = []
        query_terms = query.lower().split()
        for item in data:
            if not isinstance(item, dict) or "position" not in item:
                continue
            title = item.get("position", "")
            tags = item.get("tags", [])
            text = f"{title} {' '.join(tags)}".lower()
            if not any(term in text for term in query_terms):
                continue
            jobs.append(normalize_job(
                title=title,
                company=item.get("company", ""),
                location="Remote",
                description=item.get("description", ""),
                url=item.get("url", f"https://remoteok.com/l/{item.get('id', '')}"),
                source=self.source_name,
                posted_at=item.get("date", ""),
                remote=True,
                tags=tags,
            ))
        return jobs[:20]
