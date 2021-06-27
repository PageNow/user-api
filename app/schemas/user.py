from typing import List, Optional
import uuid
import datetime

from pydantic import BaseModel

class UserBase(BaseModel):
    first_name: str
    middle_name: str
    last_name: str

class UserPublic(UserBase):
    user_uuid: uuid.UUID
    dob: Optional[datetime.date] = None

class UserPrivate(UserPublic):
    user_id: str
    email: str
    dob_public: bool

class UserCreate(UserBase):
    dob: datetime.date
    gender: str