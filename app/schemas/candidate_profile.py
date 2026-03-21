from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CandidateProfileBase(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    headline: Optional[str] = None
    summary: Optional[str] = None

    skills: Optional[str] = None
    experience: Optional[str] = None
    projects: Optional[str] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    languages: Optional[str] = None

    work_authorization: Optional[str] = None
    visa_status: Optional[str] = None
    open_to_relocation: Optional[bool] = False
    open_to_remote: Optional[bool] = True


class CandidateProfileCreate(CandidateProfileBase):
    pass


class CandidateProfileUpdate(CandidateProfileBase):
    pass


class CandidateProfileResponse(CandidateProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateProfileParseResponse(CandidateProfileBase):
    """Response shape for parsing a CV without persisting it."""
    raw_text: Optional[str] = None
    extracted_links: Optional[List[str]] = None