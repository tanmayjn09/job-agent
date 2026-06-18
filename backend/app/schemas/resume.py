from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TailorResumeRequest(BaseModel):
    candidate_id: int
    job_id: int
    extra_description: Optional[str] = None


class TailoredResumeResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    content_json: Optional[str]
    ats_keywords: Optional[str]
    status: str
    created_at: Optional[datetime]
    pdf_ready: bool = False

    class Config:
        from_attributes = True
