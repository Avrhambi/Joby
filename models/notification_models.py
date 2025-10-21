from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class NotificationBase(BaseModel):
    id: str
    title: str
    seniority: Literal["intern", "junior", "senior", "chief"]
    country: str
    location: str
    dist: int = 0
    job_scope: Literal["parttime", "temporary", "fulltime", "full time", "part time"]
    frequency: Literal["daily", "twice_week", "weekly"]
    email_enabled: bool = True


class NotificationResponse(NotificationBase):
    last_sent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UpdateNotificationRequest(BaseModel):
    title: str
    seniority: str
    country: str
    location: str
    dist: int
    job_scope: str
    frequency: str
    email_enabled: bool
