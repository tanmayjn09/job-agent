import httpx
import re
from .base import BaseCrawler, normalize_job


class HackerNewsJobsCrawler(BaseCrawler):
    """Scrapes the monthly HN 'Who is Hiring?' thread via Algolia API."""
    source_name = "hackernews"

    async def search(self, query: str, location: str = "", **kwargs) -> list[dict]:
        query_terms = query.lower().split()
        jobs = []

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                search_res = await client.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={
                        "query": "Ask HN: Who is hiring?",
                        "tags": "story,ask_hn",
                        "hitsPerPage": 1,
                    }
                )
                hits = search_res.json().get("hits", [])
                if not hits:
                    return []
                thread_id = hits[0]["objectID"]

                comments_res = await client.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={
                        "tags": f"comment,story_{thread_id}",
                        "hitsPerPage": 100,
                    }
                )
                comments = comments_res.json().get("hits", [])

            for comment in comments:
                text = comment.get("comment_text", "") or ""
                clean = re.sub(r"<[^>]+>", " ", text)
                if not any(term in clean.lower() for term in query_terms):
                    continue

                lines = [l.strip() for l in clean.split("\n") if l.strip()]
                title_line = lines[0] if lines else "Software Engineer"
                company_match = re.search(r"\b([A-Z][a-zA-Z0-9]+(?:\s[A-Z][a-zA-Z]+)*)\b", title_line)
                company = company_match.group(1) if company_match else "HN Company"

                loc = "Remote" if "remote" in clean.lower() else (location or "Unknown")

                jobs.append(normalize_job(
                    title=title_line[:100],
                    company=company,
                    location=loc,
                    description=clean[:2000],
                    url=f"https://news.ycombinator.com/item?id={comment.get('objectID', '')}",
                    source=self.source_name,
                    posted_at=comment.get("created_at", ""),
                    remote="remote" in clean.lower(),
                ))

        except Exception:
            return []

        return jobs[:15]
