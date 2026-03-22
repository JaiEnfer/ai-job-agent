from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class ApplicationPackage(Base):
    __tablename__ = "application_packages"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False, index=True)

    parsed_job_json = Column(Text, nullable=False)
    candidate_profile_analysis_json = Column(Text, nullable=False)
    match_result_json = Column(Text, nullable=False)
    tailored_cv_json = Column(Text, nullable=False)
    cover_letter_json = Column(Text, nullable=False)
    ats_score_json = Column(Text, nullable=False)

    application_package_text = Column(Text, nullable=False)

    status = Column(String(100), nullable=False, default="generated")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Back-reference to the CandidateProfile that owns this package.
    profile = relationship(
        "CandidateProfile",
        back_populates="application_packages",
    )

    # When a package is deleted, set application_package_id to NULL on any
    # linked Application rows rather than blocking or cascading the delete.
    applications = relationship(
        "Application",
        foreign_keys="Application.application_package_id",
        back_populates="application_package",
        cascade="all, delete-orphan",
    )