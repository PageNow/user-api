import uuid
from typing import Dict
import datetime

from databases import Database
from sqlalchemy import select, text

from app.models.user import user_table
from app.schemas.user import UserCreate, UserUpdate
from app.utils.constants import DEFAULT_DOMAIN_ALLOW_ARRAY, \
    DEFAULT_DOMAIN_DENY_ARRAY, SEARCH_MAX_LIMIT
from app.core.logger import logging


async def get_user_by_id(db: Database, user_id: str):
    stmt = select([text('*')]).where(user_table.c.user_id == user_id)
    user = await db.fetch_one(stmt)
    return user


async def get_user_by_uuid(db: Database, user_uuid: uuid.UUID):
    query = user_table.select().where(user_table.c.user_uuid == user_uuid)
    user = await db.fetch_one(query)
    return user


async def get_user_by_email(db: Database, email: str):
    pass


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
        "domain_deny_array": DEFAULT_DOMAIN_DENY_ARRAY,
        "created_at": datetime.datetime.utcnow()
    })
    query = user_table.insert().values(**user_dict)
    error = None
    try:
        await db.execute(query)
    except Exception as e:
        print(e)
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
        print(e)
        error = e
    return error


async def update_profile_upload_time(
    db: Database,
    user_id: str,
    image_ext: str
):
    user_dict = {
        "profile_image_uploaded_at": datetime.datetime.utcnow(),
        "profile_image_extension": image_ext
    }
    query = (
        user_table.update()
        .where(user_table.c.user_id == user_id)
        .values(**user_dict)
    )
    error = None
    try:
        await db.execute(query)
    except Exception as e:
        print(e)
        error = e
    return error


# functions related to searching users from all users

# TODO: add limit, fetch public information only
async def search_user_by_email(
    db: Database,
    email: str,
    exact: bool,
    limit: int,
    offset: int = 0
):
    limit = min(SEARCH_MAX_LIMIT, limit)
    if exact:
        stmt = (
            select([text('*')])
            .select_from(user_table)
            .where(user_table.c.email == email)
            .limit(limit)
            .offset(offset)
        )
    else:
        stmt = (
            select([text('*')])
            .where(user_table.c.email.like(f'%{email}%'))
            .limit(10)
            .offset(offset)
        )

    users, error = None, None
    try:
        users = await db.fetch_all(stmt)
    except Exception as e:
        logging.error(e)
        error = None
    return {'users': users, 'error': error}


async def search_user_by_name(
    db: Database,
    name: str,
    exact: bool,
    limit: int,
    offset: int = 0
):
    limit = min(SEARCH_MAX_LIMIT, limit)
    if exact:
        stmt = (
            select([text('*')])
            .where(user_table.c.name == name)
            .limit(limit)
            .offset(offset)
        )
    else:
        stmt = (
            select([text('*')])
            .where(user_table.c.name.like(f'%{name}%'))
            .limit(limit)
            .offset(offset)
        )

    users, error = None, None
    try:
        users = await db.fetch_all(stmt)
    except Exception as e:
        logging.error(e)
        error = e
    return {'users': users, 'error': error}
