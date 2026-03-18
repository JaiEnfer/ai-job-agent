from pydantic import BaseModel
from typing import Optional


class ApplicationUpdate(BaseModel):
    application_package_id: Optional[int] = None
    status: Optional[str] = None
    application_channel: Optional[str] = None
    external_application_id: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    notes: Optional[str] = None
    response_notes: Optional[str] = None