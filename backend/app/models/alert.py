from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    alert_type = Column(String, default="new_match")
    match_score = Column(Float, default=0.0)
    is_read = Column(Boolean, default=False)

    job = relationship("Job")
