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
    
    description: str

    gender: Optional[str] = None
    school: Optional[str] = None
    work: Optional[str] = None
    location: Optional[str] = None
    description: str

class UserPrivate(UserPublic):
    user_id: str
    email: str
    email_public: bool
    
    dob_public: bool
    gender_public: bool
    school_public: bool
    work_public: bool
    location_public: bool
    
    share_mode: str
    domain_allow_array: list
    domain_deny_array: list

class UserCreate(UserBase):
    dob: datetime.date
    gender: str

class UserUpdate(BaseModel):
    description: str
    share_mode: str
    domain_allow_array: list[str]
    domain_deny_array: list[str]
    
    gender: str
    school: str
    work: str
    location: str

    email_public: bool
    gender_public: bool
    school_public: bool
    work_public: bool
    location_public: bool