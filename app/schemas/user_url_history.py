import datetime

from pydantic import BaseModel


class UserActivityBase(BaseModel):
    user_id: str


class UserUrlHistory(UserActivityBase):
    url: str
    page_title: str
    accessed_at: datetime.datetime


class UserUrlHistorySave(BaseModel):
    url: str
    page_title: str
