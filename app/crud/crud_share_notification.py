import datetime
from typing import List

from sqlalchemy import select

from databases import Database
from app.core.logger import logging
from app.crud import crud_friendship
from app.models.share_notification import share_notification_table
from app.models.share_notification_seen import share_notification_seen_table
from app.schemas.friendship import FriendId
from app.schemas.share_notification import ShareNotificationCreate, \
    ShareNotificationRead
from app.schemas.share_notification_seen import ShareNotificationSeenCreate

logger = logging.getLogger(__name__)


async def get_all_sharing_notifications(
    db: Database,
    curr_user_id: str
):
    user_sharing_notification_seen = (
        select([
            share_notification_seen_table.c.event_id,
            share_notification_seen_table.c.seen_at
        ])
        .select_from(share_notification_seen_table)
        .where(share_notification_seen_table.c.user_id == curr_user_id)
        .cte().alias('user_sharing_notification_seen')
    )
    query = (
        select([
            share_notification_table.c.event_id,
            share_notification_table.c.user_id,
            share_notification_table.c.timestamp,
            share_notification_table.c.url,
            share_notification_table.c.title,
            user_sharing_notification_seen.c.seen_at
        ])
        .select_from(
            share_notification_table.join(
                user_sharing_notification_seen,
                (share_notification_table.c.event_id ==
                    user_sharing_notification_seen.c.event_id)
            )
        )
    )

    notifications, error = None, None
    try:
        notifications = await db.fetch_all(query)
    except Exception as e:
        logging.error(e)
        error = e
    return {'notifications': notifications, 'error': error}


async def get_sharing_notifications(
    db: Database,
    curr_user_id: str,
    is_read: bool
):
    if is_read:
        seen_at_condition = share_notification_seen_table.c.seen_at.isnot(None)
    else:
        seen_at_condition = share_notification_seen_table.c.seen_at.is_(None)

    user_sharing_notification_seen = (
        select([
            share_notification_seen_table.c.event_id,
            share_notification_seen_table.c.seen_at
        ])
        .select_from(share_notification_seen_table)
        .where((share_notification_seen_table.c.user_id == curr_user_id)
               & seen_at_condition)
        .cte().alias('user_sharing_notification_seen')
    )
    query = (
        select([
            share_notification_table.c.event_id,
            share_notification_table.c.user_id,
            share_notification_table.c.timestamp,
            share_notification_table.c.url,
            share_notification_table.c.title,
            user_sharing_notification_seen.c.seen_at
        ])
        .select_from(
            share_notification_table.join(
                user_sharing_notification_seen,
                (share_notification_table.c.event_id ==
                    user_sharing_notification_seen.c.event_id)
            )
        )
    )

    notifications, error = None, None
    try:
        notifications = await db.fetch_all(query)
    except Exception as e:
        logging.error(e)
        error = e
    return {'notifications': notifications, 'error': error}


async def create_sharing_notification(
    db: Database,
    curr_user_id: str,
    share_notification: ShareNotificationCreate
):
    # get the list of friend ids
    user_friends_res = await crud_friendship.get_all_user_friends(
        db, curr_user_id)
    error = None
    if user_friends_res['error'] is not None:
        return error
    user_friends = user_friends_res['friends']
    friend_id_arr = list(
        map(lambda x: x['user_id'], [
            FriendId(**user_friends[i]).dict()
            for i in range(len(user_friends))
        ])
    )

    # create rows for share_notification and share_notification_seen
    # in transaction
    event_id, error = None, None
    transaction = await db.transaction()
    try:
        # create a row for new share_notification entry
        share_data = share_notification.dict()
        share_notification: ShareNotificationCreate = {
            'user_id': curr_user_id,
            'url': share_data['url'],
            'title': share_data['title']
        }
        query = share_notification_table.insert()
        event_id = await db.execute(query=query, values=share_notification)
        # create entries for share_notification_seen of all friends
        share_notification_seen_values: List[ShareNotificationSeenCreate] = [
            {'event_id': event_id, 'user_id': friend_id}
            for friend_id in friend_id_arr
        ]
        query = share_notification_seen_table.insert()
        await db.execute_many(
            query=query, values=share_notification_seen_values)
    except Exception as e:
        error = e
        logging.error(e)
        await transaction.rollback()
    else:
        await transaction.commit()
    return {'event_id': event_id, 'error': error}


async def read_sharing_notification(
    db: Database,
    curr_user_id: str,
    event_data: List[ShareNotificationRead]
):
    event_data = list(map(lambda x: x.dict(), event_data))
    event_id_list = list(map(lambda x: x['event_id'], event_data))

    update_dict = {'seen_at': datetime.datetime.utcnow()}
    query = (
        share_notification_seen_table.update()
        .where((share_notification_seen_table.c.user_id == curr_user_id)
               & share_notification_seen_table.c.event_id.in_(event_id_list))
        .values(**update_dict)
    )
    error = None
    try:
        await db.execute(query)
    except Exception as e:
        logging.error(e)
        error = e
    return error
