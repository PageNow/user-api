import datetime

from sqlalchemy import select, text
from databases import Database

from app.models.friendship import friendship_table
from app.models.user import user_table
from app.schemas.friendship import FriendshipRequest, FriendshipAccept


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
        print(e)
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
        print(e)
        error = e
    return error


async def get_friendship_requests(db: Database, curr_user_id: str):
    """ Get friendship requests that the current user has not accepted yet. """
    query = (
        friendship_table.select()
        .where(friendship_table.c.user_id2 == curr_user_id)
    )
    request_arr, error = None, None
    try:
        request_arr = await db.fetch_all(query)
    except Exception as e:
        print(e)
        error = e
    return {'request_arr': request_arr, 'error': error}


async def delete_friendship_request(
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
        res = await db.execute(query)
        print(res)
    except Exception as e:
        print(e)
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
    error = None
    try:
        res = await db.execute(query)
        print(res)
    except Exception as e:
        print(e)
        error = e
    return error


async def get_friends_by_name(
    db: Database,
    user_id: str,
    first_name: str,
    last_name: str
):
    pass


async def get_friends_by_email(
    db: Database,
    user_id: str,
    email: str,
    exact: bool,
    limit: int = 10
):
    # filter user_table with the given email to reduce join operation size
    if exact:
        user_email_table = (
            user_table.select()
            .where(user_table.c.email == email)
        )
    else:
        user_email_table = (
            user_table.select()
            .where(user_table.c.email.like(f'%{email}%'))
        )
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
        select([text('*')])
        .select_from(
            user_id1_friendship_table.join(
                user_email_table,
                user_table.c.user_id == user_id1_friendship_table.c.user_id2
            )
        )
    ).limit(limit)
    # join friendship_table user_id1 == user_table.user_id
    stmt_user_id2 = (
        select([text('*')])
        .select_from(
            user_id2_friendship_table.join(
                user_email_table,
                user_table.c.user_id == user_id2_friendship_table.c.user_id1
            )
        )
    ).limit(limit)
    res = None
    try:
        res1 = await db.fetch_all(stmt_user_id1)
        res2 = await db.fetch_all(stmt_user_id2)
        res = res1 + res2
    except Exception as e:
        print(e)

    return res
