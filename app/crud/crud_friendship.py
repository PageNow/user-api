import datetime

from sqlalchemy import select
from databases import Database

from app.models.friendship import friendship_table
from app.models.user import user_table
from app.schemas.friendship import FriendshipRequest, FriendshipAccept
from app.utils.constants import SEARCH_MAX_LIMIT
from app.core.logger import logging

logger = logging.getLogger(__name__)


async def check_friendship(
    db: Database,
    curr_user_id: str,
    user_id: str
):
    query = (
        friendship_table.select()
        .where(((friendship_table.c.user_id1 == curr_user_id)
                & (friendship_table.c.user_id2 == user_id)) |
               ((friendship_table.c.user_id1 == user_id)
                & (friendship_table.c.user_id2 == curr_user_id)))
    )
    request, error = None, None
    try:
        request = await db.fetch_one(query)
    except Exception as e:
        logging.error(e)
        error = e
    return {'request': request, 'error': error}


async def create_friendship_request(
    db: Database,
    curr_user_id: str,
    friendship_request: FriendshipRequest
):
    request_dict = friendship_request.dict()
    request_dict.update({
        'user_id1': curr_user_id,
        'requested_at': datetime.datetime.utcnow()
    })
    query = friendship_table.insert().values(**request_dict)
    error = None
    try:
        await db.execute(query)
    except Exception as e:
        logging.error(e)
        error = e
    return error


async def accept_friendship_request(
    db: Database,
    curr_user_id: str,
    friendship_accept: FriendshipAccept
):
    accept_dict = friendship_accept.dict()
    update_dict = {'accepted_at': datetime.datetime.utcnow()}
    query = (
        friendship_table.update()
        .where((friendship_table.c.user_id1 == accept_dict['user_id1']) &
               (friendship_table.c.user_id2 == curr_user_id))
        .values(**update_dict)
    )
    error = None
    try:
        await db.execute(query)
    except Exception as e:
        logging.error(e)
        error = e
    return error


async def check_friendship_request(
    db: Database,
    curr_user_id: str,
    user_id: str
):
    query = (
        friendship_table.select()
        .where((friendship_table.c.user_id1 == curr_user_id)
               & (friendship_table.c.user_id2 == user_id))
    )
    request, error = None, None
    try:
        request = await db.fetch_one(query)
    except Exception as e:
        logging.error(e)
        error = e
    return {'request': request, 'error': error}


async def get_all_friendship_requests(db: Database, curr_user_id: str):
    """ Get friendship requests that the current user has not accepted yet. """
    query = (
        friendship_table.select()
        .where((friendship_table.c.user_id2 == curr_user_id) &
               (friendship_table.c.accepted_at.is_(None)))
    )
    request_arr, error = None, None
    try:
        request_arr = await db.fetch_all(query)
    except Exception as e:
        logging.error(e)
        error = e
    return {'request_arr': request_arr, 'error': error}


async def get_all_friendship_request_users(db: Database, curr_user_id: str):
    """
    Get user summary info of users who sent friend requests but has not
    been accepted yet.
    user_id1 is the other user and user_id2 is the current user
    in friendship table.
    """
    friendship_table_filtered = (
        friendship_table.select()
        .where((friendship_table.c.user_id2 == curr_user_id) &
               (friendship_table.c.accepted_at.is_(None)))
    ).alias('friendship_table_filtered')
    query = (
        select([
            user_table.c.user_id, user_table.c.user_uuid,
            user_table.c.first_name, user_table.c.middle_name,
            user_table.c.last_name, user_table.c.description,
            user_table.c.profile_image_uploaded_at,
            user_table.c.profile_image_extension
        ])
        .select_from(
            user_table.join(
                friendship_table_filtered,
                friendship_table_filtered.c.user_id1 == user_table.c.user_id
            )
        )
    )
    users, error = None, None
    try:
        users = await db.fetch_all(query)
    except Exception as e:
        logging.error(e)
        error = e
    return {'users': users, 'error': error}


async def delete_friendship(
    db: Database,
    user_id1: str,
    user_id2: str
):
    query = (
        friendship_table.delete()
        .where((friendship_table.c.user_id1 == user_id1) &
               (friendship_table.c.user_id2 == user_id2))
    )
    error = None
    try:
        await db.execute(query)
    except Exception as e:
        logging.error(e)
        error = e
    return error


# functions related to getting friends (used for search, etc.)
async def get_all_friends(db: Database, user_id: str):
    query = (
        friendship_table.select()
        .where(((friendship_table.c.user_id1 == user_id) |
               (friendship_table.c.user_id2 == user_id)) &
               (friendship_table.c.accepted_at is not None))
    )
    friends, error = None, None
    try:
        friends = await db.execute(query)
    except Exception as e:
        logging.error(e)
        error = e
    return {'friends': friends, 'error': error}


async def get_friends_by_name(
    db: Database,
    user_id: str,
    name: str,
    exact: bool,
    limit: int,
    offset: int = 0
):
    pass


async def get_friends_by_email(
    db: Database,
    user_id: str,
    email: str,
    exact: bool,
    limit: int,
    offset: int = 0
):
    limit = min(SEARCH_MAX_LIMIT, limit)
    # filter user_table with the given email to reduce join operation size
    if exact:
        user_email_table = (
            user_table.select()
            .where(user_table.c.email == email)
        ).alias("user_email_table")
    else:
        user_email_table = (
            user_table.select()
            .where(user_table.c.email.like(f'%{email}%'))
            .limit(100)
        ).alias("user_email_table")
    # friends of user whose user_id == user_id1 (user_id1 is user_id)
    user_id1_friendship_table = (
        friendship_table.select()
        .where(friendship_table.c.user_id1 == user_id)
    ).alias("user_id1_friendship_table")
    # friends of user whose user_id == user_id2 (user_id2 is user_id)
    user_id2_friendship_table = (
        friendship_table.select()
        .where(friendship_table.c.user_id2 == user_id)
    ).alias("user_id2_friendship_table")
    # join friendship_table user_id2 == user_table.user_id
    stmt_user_id1 = (
        select([
            user_email_table.c.user_id, user_email_table.c.user_uuid,
            user_email_table.c.first_name, user_email_table.c.middle_name,
            user_email_table.c.last_name, user_email_table.c.description,
            user_email_table.c.profile_image_uploaded_at,
            user_email_table.c.profile_image_extension
        ])
        .select_from(
            user_id1_friendship_table.join(
                user_email_table,
                user_email_table.c.user_id
                == user_id1_friendship_table.c.user_id2
            )
        )
        .limit(limit)
        .offset(offset)
    )
    # join friendship_table user_id1 == user_table.user_id
    stmt_user_id2 = (
        select([
            user_email_table.c.user_id, user_email_table.c.user_uuid,
            user_email_table.c.first_name, user_email_table.c.middle_name,
            user_email_table.c.last_name, user_email_table.c.description,
            user_email_table.c.profile_image_uploaded_at,
            user_email_table.c.profile_image_extension
        ])
        .select_from(
            user_id2_friendship_table.join(
                user_email_table,
                user_email_table.c.user_id
                == user_id2_friendship_table.c.user_id1
            )
        )
        .limit(limit)
        .offset(offset)
    )
    friends, error = None, None
    try:
        res1 = await db.fetch_all(stmt_user_id1)
        res2 = await db.fetch_all(stmt_user_id2)
        friends = res1 + res2
    except Exception as e:
        logging.error(e)
        error = e
    return {'friends': friends, 'error': error}
