from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobSearchFilters(BaseModel):
    candidate_id: int
    query: Optional[str] = None
    locations: Optional[List[str]] = []
    remote: Optional[bool] = None
    date_posted: Optional[str] = "month"
    seniority: Optional[str] = None
    industries: Optional[List[str]] = []
    employment_type: Optional[str] = None
    page: Optional[int] = 1
    per_page: Optional[int] = 20


class JobResponse(BaseModel):
    id: int
    title: str
    company: Optional[str]
    location: Optional[str]
    description: Optional[str]
    url: Optional[str]
    source: Optional[str]
    posted_at: Optional[str]
    remote: bool
    seniority: Optional[str]
    industry: Optional[str]
    employment_type: Optional[str]

    class Config:
        from_attributes = True


class JobMatchResponse(BaseModel):
    id: int
    job: JobResponse
    match_score: float
    match_reasoning: Optional[str]
    skill_matches: Optional[str]
    skill_gaps: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class JobSearchResponse(BaseModel):
    matches: List[JobMatchResponse]
    total: int
    page: int
    per_page: int
