import httpx
import xml.etree.ElementTree as ET
from .base import BaseCrawler, normalize_job

RSS_FEEDS = [
    "https://weworkremotely.com/remote-jobs.rss",
    "https://weworkremotely.com/categories/remote-programming-jobs.rss",
    "https://weworkremotely.com/categories/remote-marketing-jobs.rss",
    "https://weworkremotely.com/categories/remote-product-jobs.rss",
    "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
    "https://weworkremotely.com/categories/remote-design-jobs.rss",
    "https://weworkremotely.com/categories/remote-sales-jobs.rss",
]


class WeWorkRemotelyCrawler(BaseCrawler):
    source_name = "weworkremotely"

    async def search(self, query: str, location: str = "", **kwargs) -> list[dict]:
        query_terms = query.lower().split()
        jobs = []
        headers = {"User-Agent": "Mozilla/5.0"}

        async with httpx.AsyncClient(timeout=15) as client:
            for feed_url in RSS_FEEDS[:3]:
                try:
                    res = await client.get(feed_url, headers=headers)
                    root = ET.fromstring(res.text)
                    channel = root.find("channel")
                    if not channel:
                        continue
                    for item in channel.findall("item"):
                        title_el = item.find("title")
                        link_el = item.find("link")
                        desc_el = item.find("description")
                        pub_el = item.find("pubDate")
                        if title_el is None:
                            continue
                        raw = title_el.text or ""
                        parts = raw.split(": ", 1)
                        company = parts[0].strip() if len(parts) > 1 else ""
                        title = parts[1].strip() if len(parts) > 1 else raw
                        text = f"{title} {company}".lower()
                        if not any(t in text for t in query_terms):
                            continue
                        jobs.append(normalize_job(
                            title=title,
                            company=company,
                            location="Remote",
                            description=desc_el.text or "" if desc_el is not None else "",
                            url=link_el.text or "" if link_el is not None else "",
                            source=self.source_name,
                            posted_at=pub_el.text or "" if pub_el is not None else "",
                            remote=True,
                        ))
                except Exception:
                    continue

        return jobs[:20]
