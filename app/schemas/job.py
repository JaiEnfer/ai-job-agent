from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class JobBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    source: Optional[str] = None
    job_url: Optional[str] = None
    description: str


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True