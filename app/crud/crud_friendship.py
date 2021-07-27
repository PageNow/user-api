import datetime

from databases import Database

from app.models.friendship import friendship_table
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
