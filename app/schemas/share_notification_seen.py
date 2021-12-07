import uuid

from pydantic import BaseModel


class ShareNotificationSeenCreate(BaseModel):
    event_id: uuid.UUID
    user_id: str
