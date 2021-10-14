from typing import List, Optional
import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    first_name: str
    middle_name: str
    last_name: str


class UserSummary(UserBase):
    user_id: str
    description: str

    profile_image_uploaded_at: Optional[datetime.datetime] = None
    profile_image_extension: Optional[str] = None


class UserPublic(UserSummary):
    dob: Optional[datetime.date] = None

    gender: Optional[str] = None
    school: Optional[str] = None
    work: Optional[str] = None
    location: Optional[str] = None


class UserPrivate(UserPublic):
    email: str
    email_public: bool

    dob_public: bool
    gender_public: bool
    school_public: bool
    work_public: bool
    location_public: bool

    share_mode: str
    domain_allow_array: List
    domain_deny_array: List


class UserCreate(UserBase):
    dob: datetime.date
    gender: str


class UserUpdate(UserBase):
    description: str
    share_mode: str
    domain_allow_array: List[str]
    domain_deny_array: List[str]

    gender: str
    school: str
    work: str
    location: str

    email_public: bool
    gender_public: bool
    school_public: bool
    work_public: bool
    location_public: bool
