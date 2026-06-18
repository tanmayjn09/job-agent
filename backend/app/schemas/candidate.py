from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ExpectationsSchema(BaseModel):
    target_role: Optional[str] = None
    seniority: Optional[str] = None
    locations: Optional[List[str]] = []
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    remote_preference: Optional[str] = "any"
    industries: Optional[List[str]] = []
    employment_types: Optional[List[str]] = ["full-time"]


class CandidateOnboardResponse(BaseModel):
    id: int
    name: Optional[str]
    email: Optional[str]
    profile_json: Optional[str]
    message: str

    class Config:
        from_attributes = True


class CandidateProfileUpdate(BaseModel):
    profile_json: Optional[str] = None
    expectations_json: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    about_text: Optional[str] = None


class CandidateResponse(BaseModel):
    id: int
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    profile_json: Optional[str]
    expectations_json: Optional[str]
    github_url: Optional[str]
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    about_text: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    candidate: CandidateResponse
    total_job_matches: int
    total_resumes_generated: int
    avg_match_score: float
    recent_matches: List[dict]
    recent_resumes: List[dict]
