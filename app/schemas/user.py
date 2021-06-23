from typing import List, Optional
import uuid
import datetime

from pydantic import BaseModel

class UserBase(BaseModel):
    user_id: str
    email: str
    first_name: str
    middle_name: str
    last_name: str

class User(UserBase):
    user_uuid: uuid.UUID
    dob: Optional[datetime.date] = None

class UserCreate(UserBase):
    dob: datetime.date