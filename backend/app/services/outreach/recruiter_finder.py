"""
Finds hiring manager / recruiter for a company + role via Google search.
Uses site:linkedin.com search to find relevant profiles.
"""
import httpx
import re
from bs4 import BeautifulSoup


async def find_hiring_manager(company: str, job_title: str) -> dict:
    queries = [
        f'site:linkedin.com/in "{company}" "hiring manager" "{job_title}"',
        f'site:linkedin.com/in "{company}" recruiter "{job_title}"',
        f'site:linkedin.com/in "{company}" "head of engineering" OR "engineering manager" OR "vp engineering"',
    ]
    for query in queries:
        result = await _google_linkedin_search(query)
        if result:
            return result
    return {}


async def _google_linkedin_search(query: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            res = await client.get(
                "https://www.google.com/search",
                params={"q": query, "num": 3},
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Accept": "text/html",
                },
            )
        soup = BeautifulSoup(res.text, "html.parser")
        for result in soup.find_all("div", class_="g")[:3]:
            link_el = result.find("a", href=True)
            title_el = result.find("h3")
            snippet_el = result.find("span", class_=lambda c: c and "st" in (c or ""))
            if not link_el or not title_el:
                continue
            url = link_el["href"]
            if "linkedin.com/in/" not in url:
                continue
            name = title_el.get_text(strip=True).split(" - ")[0].split(" | ")[0]
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""
            return {
                "name": name,
                "linkedin_url": url,
                "snippet": snippet,
                "found": True,
            }
    except Exception:
        pass
    return {}
