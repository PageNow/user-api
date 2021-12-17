from typing import Optional
import uuid
import datetime

from pydantic import BaseModel


class ShareNotificationCreate(BaseModel):
    url: str
    title: str
    sent_to: Optional[str] = None


class ShareNotificationRead(BaseModel):
    event_id: uuid.UUID


class ShareNotificationsSent(ShareNotificationCreate):
    event_id: uuid.UUID
    sent_at: datetime.datetime
    not_seen_count: int
    sent_to: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    profile_image_extension: Optional[str]
