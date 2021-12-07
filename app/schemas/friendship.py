from typing import Optional
import datetime

from pydantic import BaseModel


class FriendshipBase(BaseModel):
    user_id1: str
    user_id2: str


class FriendshipRequest(BaseModel):
    user_id2: str


class FriendshipAccept(BaseModel):
    user_id1: str


class FriendshipDelete(BaseModel):
    user_id1: str
    user_id2: str


class FriendshipInfo(FriendshipBase):
    requested_at: datetime.datetime
    accepted_at: Optional[datetime.datetime]


class FriendId(BaseModel):
    user_id: str
