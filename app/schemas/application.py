from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApplicationCreate(BaseModel):
    job_id: int
    profile_id: int
    application_package_id: Optional[int] = None
    status: Optional[str] = "draft"
    application_channel: Optional[str] = None
    external_application_id: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    notes: Optional[str] = None
    response_notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    profile_id: int
    application_package_id: Optional[int] = None
    status: str
    applied_at: Optional[datetime] = None
    application_channel: Optional[str] = None
    external_application_id: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    notes: Optional[str] = None
    response_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True