from typing import Dict, List
import datetime

from databases import Database
from sqlalchemy import select, text, case, union, Integer
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
async def search_user_with_email(
    db: Database,
    # curr_user: Dict[str, str],
    email: str,
    limit: int,
    offset: int = 0
):
    limit = min(SEARCH_MAX_LIMIT, limit)
    # user_id = curr_user["user_id"]
    user_id = '543449a2-9225-479e-bf0c-c50da6b16b7c'

    # get friends of user_id (user_id, accepted_state)
    friends1 = (
        select([
            friendship_table.c.user_id2.label("user_id"),
            case(
                [(friendship_table.c.accepted_at.isnot(None),
                  cast(literal(2), Integer))],
                else_=cast(literal(1), Integer)
            ).label("accepted_state")
        ])
        .select_from(friendship_table)
        .where(friendship_table.c.user_id1 == user_id)
    )
    friends2 = (
        select([
            friendship_table.c.user_id1.label("user_id"),
            case(
                [(friendship_table.c.accepted_at.isnot(None),
                  cast(literal(2), Integer))],
                else_=cast(literal(1), Integer)
            ).label("accepted_state")
        ])
        .select_from(friendship_table)
        .where(friendship_table.c.user_id2 == user_id)
    )
    friends = friends1.union_all(friends2).alias('friends')

    # get user_ids filtered using email
    # match score 3 - match from start, 2 - match from end, 1 - match in middle
    user_id_filtered3 = (
        select([
            user_table.c.user_id,
            cast(literal(3), Integer).label("match_score")
        ])
        .select_from(user_table)
        .where(user_table.c.email.like(f'{email}%'))
    )
    user_id_filtered2 = (
        select([
            user_table.c.user_id,
            cast(literal(2), Integer).label("match_score")
        ])
        .select_from(user_table)
        .where(user_table.c.email.like(f'%{email}'))
    )
    user_id_filtered1 = (
        select([
            user_table.c.user_id,
            cast(literal(1), Integer).label("match_score")
        ])
        .select_from(user_table)
        .where(user_table.c.email.like(f'%{email}%'))
    )
    user_id_filtered321 = union(user_id_filtered3, user_id_filtered2,
                                user_id_filtered1).alias('user_id_filtered321')
    user_id_filtered = (
        select([
            user_id_filtered321.c.user_id.label("user_id"),
            max_(user_id_filtered321.c.match_score).label("match_score")
        ])
        .select_from(user_id_filtered321)
        .group_by(user_id_filtered321.c.user_id)
    ).alias("user_id_filtered")

    # actual query
    query_table = (
        select([
            user_table.c.user_id, user_table.c.first_name,
            user_table.c.last_name, user_table.c.description,
            user_table.c.profile_image_extension,
            friends.c.accepted_state, user_id_filtered.c.match_score
        ])
        .select_from(
            user_table.join(
                user_id_filtered,
                user_table.c.user_id == user_id_filtered.c.user_id,
            ).join(
                friends,
                user_table.c.user_id == friends.c.user_id,
                isouter=True,
                full=True
            )
        )
        .where(user_table.c.user_id.isnot(None))
    ).alias('query_table')

    # get user_id
    query = (
        select([
            query_table.c.user_id, query_table.c.first_name,
            query_table.c.last_name, query_table.c.description,
            query_table.c.profile_image_extension,
            coalesce(query_table.c.accepted_state, 0).label("accepted_state"),
            query_table.c.match_score
        ])
        .select_from(query_table)
        .order_by(query_table.c.accepted_state.desc().nullslast())
        .order_by(query_table.c.match_score.desc())
        .order_by(query_table.c.user_id.desc())
        .offset(offset)
        .limit(limit)
    )
    users, error = None, None
    try:
        users = await db.fetch_all(query)
    except Exception as e:
        logging.error(e)
        error = e
    return {'users': users, 'error': error}


async def search_user_by_name(
    db: Database,
    curr_user: Dict[str, str],
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
