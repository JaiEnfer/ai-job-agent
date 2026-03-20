from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)

    headline = Column(String(500), nullable=True)
    summary = Column(Text, nullable=True)

    skills = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    projects = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    certifications = Column(Text, nullable=True)
    languages = Column(Text, nullable=True)

    target_roles = Column(Text, nullable=True)
    preferred_locations = Column(Text, nullable=True)

    work_authorization = Column(String(255), nullable=True)
    visa_status = Column(String(255), nullable=True)
    open_to_relocation = Column(Boolean, default=False)
    open_to_remote = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # When a CandidateProfile is deleted, all linked ApplicationPackages are
    # automatically deleted too (cascade). This prevents the ForeignKeyViolation
    # error that occurs when trying to delete a profile that still has packages.
    application_packages = relationship(
        "ApplicationPackage",
        cascade="all, delete-orphan",
        back_populates="profile",
    )