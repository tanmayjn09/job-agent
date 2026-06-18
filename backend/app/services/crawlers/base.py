import hashlib
from abc import ABC, abstractmethod


def job_hash(title: str, company: str, location: str) -> str:
    key = f"{title.lower().strip()}-{company.lower().strip()}-{location.lower().strip()}"
    return hashlib.md5(key.encode()).hexdigest()


def normalize_job(
    title: str,
    company: str,
    location: str,
    description: str,
    url: str,
    source: str,
    posted_at: str = "",
    remote: bool = False,
    employment_type: str = "",
    salary_min: int = None,
    salary_max: int = None,
    tags: list = None,
) -> dict:
    return {
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "url": url,
        "source": source,
        "posted_at": posted_at,
        "remote": remote or "remote" in location.lower(),
        "employment_type": employment_type,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "tags": tags or [],
        "_hash": job_hash(title, company, location),
    }


class BaseCrawler(ABC):
    source_name: str = "unknown"

    @abstractmethod
    async def search(self, query: str, location: str = "", **kwargs) -> list[dict]:
        pass
