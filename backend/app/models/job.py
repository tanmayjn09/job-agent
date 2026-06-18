from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())

    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    source = Column(String, nullable=True)
    posted_at = Column(String, nullable=True)
    remote = Column(Boolean, default=False)
    seniority = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    employment_type = Column(String, nullable=True)

    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    tailored_resumes = relationship("TailoredResume", back_populates="job", cascade="all, delete-orphan")


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    match_score = Column(Float, nullable=False, default=0.0)
    match_reasoning = Column(Text, nullable=True)
    skill_matches = Column(Text, nullable=True)
    skill_gaps = Column(Text, nullable=True)
    intelligence_json = Column(Text, nullable=True)
    priority_score = Column(Float, nullable=True)

    candidate = relationship("Candidate", back_populates="job_matches")
    job = relationship("Job", back_populates="matches")
