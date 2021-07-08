import uuid
from typing import Dict
import datetime

from sqlalchemy.sql.expression import literal_column
from databases import Database

from app.models.user import user_table
from app.schemas.user import UserCreate, UserUpdate
from app.utils.constants import DEFAULT_DOMAIN_ALLOW_ARRAY, \
    DEFAULT_DOMAIN_DENY_ARRAY

async def get_user_by_id(db: Database, user_id: str):
    query = user_table.select().where(user_table.c.user_id == user_id)
    user = await db.fetch_one(query)
    return user

async def get_user_by_uuid(db: Database, user_uuid: uuid.UUID):
    query = user_table.select().where(user_table.c.user_uuid == user_uuid)
    user = await db.fetch_one(query)
    return user

async def create_user(
    db: Database,
    curr_user: Dict[str, str],
    user: UserCreate
):
    user_dict = user.dict()
    user_dict.update(curr_user)
    # add initial domain arrays
    user_dict.update({
        "domain_allow_array": DEFAULT_DOMAIN_ALLOW_ARRAY,
        "domain_deny_array": DEFAULT_DOMAIN_DENY_ARRAY
    })
    query = user_table.insert().values(**user_dict)
    error = None
    try:
        await db.execute(query)
    except Exception as e:
        error = e
    return error

async def update_user(
    db: Database,
    curr_user: Dict[str, str],
    user: UserUpdate
):
    user_dict = user.dict()
    user_dict.update(curr_user)
    query = (
        user_table.update()
        .where(user_table.c.user_id == curr_user['user_id'])
        .values(**user_dict)
    )
    error = None
    try:
        await db.execute(query)
    except Exception as e:
        error = e
    return error

async def update_profile_upload_time(db: Database, user_id: str):
    user_dict = {"profile_image_uploaded_at": datetime.datetime.utcnow()}
    query = (
        user_table.update()
        .where(user_table.c.user_id == user_id)
        .values(**user_dict)
    )
    error = None
    try:
        await db.execute(query)
    except Exception as e:
        error = e
    return error