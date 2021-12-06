import uuid

from pydantic import BaseModel


class ShareNotificationBase(BaseModel):
    user_id: str
    url: str
    title: str


class ShareNotificationRead(BaseModel):
    event_id: uuid.UUID
