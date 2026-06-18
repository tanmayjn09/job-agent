from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class TailoredResume(Base):
    __tablename__ = "tailored_resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    content_json = Column(Text, nullable=True)
    pdf_path = Column(String, nullable=True)
    ats_keywords = Column(Text, nullable=True)
    status = Column(String, default="pending")

    candidate = relationship("Candidate", back_populates="tailored_resumes")
    job = relationship("Job", back_populates="tailored_resumes")
