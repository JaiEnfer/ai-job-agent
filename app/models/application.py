from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False, index=True)
    application_package_id = Column(Integer, ForeignKey("application_packages.id"), nullable=True, index=True)

    status = Column(String(100), nullable=False, default="draft")
    applied_at = Column(DateTime(timezone=True), nullable=True)

    application_channel = Column(String(255), nullable=True)
    external_application_id = Column(String(255), nullable=True)

    recruiter_name = Column(String(255), nullable=True)
    recruiter_email = Column(String(255), nullable=True)

    notes = Column(Text, nullable=True)
    response_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())