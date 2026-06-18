from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class OutreachDraft(Base):
    __tablename__ = "outreach_drafts"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    hiring_manager_name = Column(String, nullable=True)
    hiring_manager_linkedin = Column(String, nullable=True)
    hiring_manager_email = Column(String, nullable=True)
    email_confidence = Column(Integer, default=0)

    linkedin_note = Column(Text, nullable=True)
    email_subject = Column(String, nullable=True)
    cold_email = Column(Text, nullable=True)
    follow_up_day3 = Column(Text, nullable=True)
    follow_up_day7 = Column(Text, nullable=True)
    talking_points = Column(Text, nullable=True)

    company_signals = Column(Text, nullable=True)
    status = Column(String, default="draft")

    job = relationship("Job")
