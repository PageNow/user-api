import uuid

from pydantic import BaseModel


class ShareNotificationCreate(BaseModel):
    url: str
    title: str


class ShareNotificationRead(BaseModel):
    event_id: uuid.UUID
