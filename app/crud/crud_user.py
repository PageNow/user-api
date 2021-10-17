from typing import Dict, List
import datetime

from databases import Database
from sqlalchemy import select, text, case, union, func, Integer, String
from sqlalchemy.sql.functions import coalesce, max as max_
from sqlalchemy.sql.expression import literal, cast

from app.models.user import user_table
from app.models.friendship import friendship_table
from app.schemas.user import UserCreate, UserUpdate
from app.utils.constants import DEFAULT_DOMAIN_ALLOW_ARRAY, \
    DEFAULT_DOMAIN_DENY_ARRAY, SEARCH_MAX_LIMIT
from app.core.logger import logging


async def get_user_by_id(db: Database, user_id: str):
    stmt = (
        select([text('*')])
        .select_from(user_table)
        .where(user_table.c.user_id == user_id)
    )
    user = await db.fetch_one(stmt)
    return user


async def get_user_by_email(db: Database, email: str):
    pass


async def get_users_by_id(db: Database, user_id_arr: List[str]):
    stmt = (
        select([text('*')])
        .select_from(user_table)
        .where(user_table.c.user_id.in_(tuple(user_id_arr)))
    )
    user_arr = await db.fetch_all(stmt)
    return user_arr


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


async def delete_profile_image_info(
    db: Database,
    user_id: str
):
    user_dict = {
        "profile_image_uploaded_at": None,
        "profile_image_extension": None
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
async def search_user(
    db: Database,
    # curr_user: Dict[str, str],
    search_option: str,  # email or name
    search_filter: str,
    limit: int = None,
    offset: int = 0
):
    assert search_option in ('email', 'name')

    # user_id = curr_user["user_id"]
    user_id = '543449a2-9225-479e-bf0c-c50da6b16b7c'

    search_filter = search_filter.lower()
    if limit is not None:
        limit = min(SEARCH_MAX_LIMIT, limit)

    # get friends of user_id (user_id, friendship_state)
    user_friends1 = (
        select([
            friendship_table.c.user_id2.label("user_id"),
            case(
                [(friendship_table.c.accepted_at.isnot(None),
                  cast(literal(2), Integer))],
                else_=cast(literal(1), Integer)
            ).label("friendship_state")
        ])
        .select_from(friendship_table)
        .where(friendship_table.c.user_id1 == user_id)
    )
    user_friends2 = (
        select([
            friendship_table.c.user_id1.label("user_id"),
            case(
                [(friendship_table.c.accepted_at.isnot(None),
                  cast(literal(2), Integer))],
                else_=cast(literal(1), Integer)
            ).label("friendship_state")
        ])
        .select_from(friendship_table)
        .where(friendship_table.c.user_id2 == user_id)
    )
    user_friends = (
        union(user_friends1, user_friends2).cte().alias('user_firends')
    )

    # get accepted friends of user_id (user_id)
    user_friends_accepted = (
        select([user_friends.c.user_id])
        .select_from(user_friends)
        .where(user_friends.c.friendship_state == 2)
    ).cte().alias('user_friends_accepted')

    # get all friendships that are accepted (user_id1, user_id2)
    friends = (
        select([friendship_table.c.user_id1, friendship_table.c.user_id2])
        .select_from(friendship_table)
        .where(friendship_table.c.accepted_at.isnot(None))
    ).cte().alias('friends')

    # get user_ids filtered using email
    # match score 3 - match from start, 2 - match from end, 1 - match in middle
    if search_option == 'email':
        user_id_filtered3 = (
            select([
                user_table.c.user_id,
                cast(literal(3), Integer).label("match_score")
            ])
            .select_from(user_table)
            .where(func.lower(user_table.c.email).like(f'{search_filter}%'))
        )
        user_id_filtered2 = (
            select([
                user_table.c.user_id,
                cast(literal(2), Integer).label("match_score")
            ])
            .select_from(user_table)
            .where(func.lower(user_table.c.email).like(f'%{search_filter}'))
        )
        user_id_filtered1 = (
            select([
                user_table.c.user_id,
                cast(literal(1), Integer).label("match_score")
            ])
            .select_from(user_table)
            .where(func.lower(user_table.c.email).like(f'%{search_filter}%'))
        )
    elif search_option == 'name':
        user_id_filtered3 = (
            select([
                user_table.c.user_id,
                cast(literal(3), Integer).label("match_score")
            ])
            .select_from(user_table)
            .where(func.lower(func.concat(
                user_table.c.first_name, cast(literal(' '), String),
                user_table.c.last_name)
            ).like(f'{search_filter}%'))
        )
        user_id_filtered2 = (
            select([
                user_table.c.user_id,
                cast(literal(2), Integer).label("match_score")
            ])
            .select_from(user_table)
            .where(func.lower(func.concat(
                user_table.c.first_name, cast(literal(' '), String),
                user_table.c.last_name)
            ).like(f'%{search_filter}'))
        )
        user_id_filtered1 = (
            select([
                user_table.c.user_id,
                cast(literal(1), Integer).label("match_score")
            ])
            .select_from(user_table)
            .where(func.lower(func.concat(
                user_table.c.first_name, cast(literal(' '), String),
                user_table.c.last_name)
            ).like(f'%{search_filter}%'))
        )

    user_id_filtered321 = union(user_id_filtered3, user_id_filtered2,
                                user_id_filtered1).alias('user_id_filtered321')
    user_id_filtered = (
        select([
            user_id_filtered321.c.user_id.label("user_id"),
            max_(user_id_filtered321.c.match_score).label("match_score")
        ])
        .select_from(user_id_filtered321)
        .where(user_id_filtered321.c.user_id != user_id)
        .group_by(user_id_filtered321.c.user_id)
    ).cte().alias("user_id_filtered")

    # search_result - all fields based on query conditions
    # (used as basis of later queries)
    search_result = (
        select([
            user_table.c.user_id, user_table.c.first_name,
            user_table.c.last_name, user_table.c.description,
            user_table.c.profile_image_extension,
            coalesce(user_friends.c.friendship_state, 0).label(
                'friendship_state'),
            user_id_filtered.c.match_score
        ])
        .select_from(
            user_table.join(
                user_id_filtered,
                user_table.c.user_id == user_id_filtered.c.user_id,
            ).join(
                user_friends,
                user_table.c.user_id == user_friends.c.user_id,
                isouter=True,
                full=True
            )
        )
        .where(user_table.c.user_id.isnot(None))
    ).cte().alias('search_result')

    # search_result joined with friends of each user
    # joined on user_id1
    search_result_friends1 = (
        select([
            search_result.c.user_id, search_result.c.first_name,
            search_result.c.last_name, search_result.c.description,
            search_result.c.profile_image_extension,
            search_result.c.friendship_state, search_result.c.match_score,
            friends.c.user_id2.label('friend_id')
        ])
        .select_from(
            search_result.join(
                friends, search_result.c.user_id == friends.c.user_id1,
                isouter=True, full=True
            )
        )
        .where(search_result.c.user_id.isnot(None))
    )
    # joined on user_id2
    search_result_friends2 = (
        select([
            search_result.c.user_id, search_result.c.first_name,
            search_result.c.last_name, search_result.c.description,
            search_result.c.profile_image_extension,
            search_result.c.friendship_state, search_result.c.match_score,
            friends.c.user_id1.label('friend_id')
        ])
        .select_from(
            search_result.join(
                friends, search_result.c.user_id == friends.c.user_id2,
                isouter=True, full=True
            )
        )
        .where(search_result.c.user_id.isnot(None))
    )
    # union of tow partial tables
    search_result_friends = (
        union(search_result_friends1, search_result_friends2)
    ).cte().alias('search_result_friends')

    # add a column of number of mutual friends to search_result_with_friends
    search_result_mutual_friends = (
        select([
            search_result_friends.c.user_id,
            func.count(search_result_friends.c.friend_id)
                .label('mutual_friend_count')
        ])
        .select_from(
            search_result_friends.join(
                user_friends_accepted,
                search_result_friends.c.friend_id
                == user_friends_accepted.c.user_id
            )
        )
        .group_by(search_result_friends.c.user_id)
    ).cte().alias('search_result_mutual_friends')

    query = (
        select([
            search_result.c.user_id, search_result.c.first_name,
            search_result.c.last_name, search_result.c.description,
            search_result.c.profile_image_extension,
            search_result.c.friendship_state,
            search_result.c.match_score,
            coalesce(
                search_result_mutual_friends.c.mutual_friend_count, 0
            ).label('mutual_friend_count')
        ])
        .select_from(
            search_result.join(
                search_result_mutual_friends,
                search_result.c.user_id
                == search_result_mutual_friends.c.user_id,
                isouter=True, full=True
            )
        )
        .order_by(search_result.c.friendship_state.desc().nullslast())
        .order_by(search_result_mutual_friends.c.mutual_friend_count.desc()
                  .nullslast())
        .order_by(search_result.c.match_score.desc().nullslast())
        .order_by(search_result.c.user_id.desc().nullslast())
        .offset(offset)
    )
    if limit is not None:
        query = query.limit(limit)

    users, error = None, None
    try:
        users = await db.fetch_all(query)
    except Exception as e:
        logging.error(e)
        error = e
    return {'users': users, 'error': error}
