from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    raw_resume_text = Column(Text, nullable=True)
    profile_json = Column(Text, nullable=True)
    expectations_json = Column(Text, nullable=True)

    github_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    resume_file_path = Column(String, nullable=True)
    about_text = Column(Text, nullable=True)

    files = relationship("CandidateFile", back_populates="candidate", cascade="all, delete-orphan")
    job_matches = relationship("JobMatch", back_populates="candidate", cascade="all, delete-orphan")
    tailored_resumes = relationship("TailoredResume", back_populates="candidate", cascade="all, delete-orphan")


class CandidateFile(Base):
    __tablename__ = "candidate_files"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    original_filename = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    extracted_text = Column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="files")
