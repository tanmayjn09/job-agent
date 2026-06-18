import httpx
from .base import BaseCrawler, normalize_job


class RemotiveCrawler(BaseCrawler):
    source_name = "remotive"

    async def search(self, query: str, location: str = "", **kwargs) -> list[dict]:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                res = await client.get(
                    "https://remotive.com/api/remote-jobs",
                    params={"search": query, "limit": 20},
                )
                data = res.json()
        except Exception:
            return []

        jobs = []
        query_terms = set(query.lower().split())
        for item in data.get("jobs", []):
            title = item.get("title", "")
            if not any(t in title.lower() for t in query_terms):
                continue
            jobs.append(normalize_job(
                title=title,
                company=item.get("company_name", ""),
                location=item.get("candidate_required_location", "Remote"),
                description=item.get("description", "")[:1000],
                url=item.get("url", ""),
                source=self.source_name,
                posted_at=item.get("publication_date", "")[:10],
                remote=True,
                tags=item.get("tags", []),
            ))
        return jobs[:20]
