from typing import Dict, List
import datetime

from databases import Database
from sqlalchemy import select, text, case, union, func, Integer, String
from sqlalchemy.sql.functions import coalesce, count, max as max_
from sqlalchemy.sql.expression import literal, cast

from app.models.user import user_table
from app.models.friendship import friendship_table
from app.schemas.user import UserBase, UserUpdate
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
    user: UserBase
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


async def update_domain_array(
    db: Database,
    curr_user: Dict[str, str],
    domain_array: List[str],
    share_type: str  # 'allow' or 'deny'
):
    if share_type == 'allow':
        user_dict = {
            "domain_allow_array": domain_array
        }
    elif share_type == 'deny':
        user_dict = {
            "domain_deny_array": domain_array
        }
    else:
        return "Invalid share_type"

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


async def get_mutual_friends(
    db: Database,
    curr_user: Dict[str, str],
    user_id: str,
    limit: int = SEARCH_MAX_LIMIT,
    offset: int = 0
):
    """ Get mutual friends between current user and input user """
    curr_user_id = curr_user["user_id"]
    limit = min(SEARCH_MAX_LIMIT, limit)
    curr_user_friends1 = (
        select([
            friendship_table.c.user_id1.label('friend_id')
        ])
        .select_from(friendship_table)
        .where((friendship_table.c.user_id2 == curr_user_id)
               & friendship_table.c.accepted_at.isnot(None))
    )
    curr_user_friends2 = (
        select([
            friendship_table.c.user_id2.label('friend_id')
        ])
        .select_from(friendship_table)
        .where((friendship_table.c.user_id1 == curr_user_id)
               & friendship_table.c.accepted_at.isnot(None))
    )
    curr_user_friends = union(
        curr_user_friends1, curr_user_friends2
    ).cte().alias('curr_user_friends')

    user_friends1 = (
        select([
            friendship_table.c.user_id1.label('friend_id')
        ])
        .select_from(friendship_table)
        .where((friendship_table.c.user_id2 == user_id)
               & friendship_table.c.accepted_at.isnot(None))
    )
    user_friends2 = (
        select([
            friendship_table.c.user_id2.label('friend_id')
        ])
        .select_from(friendship_table)
        .where((friendship_table.c.user_id1 == user_id)
               & friendship_table.c.accepted_at.isnot(None))
    )
    user_friends = union(
        user_friends1, user_friends2
    ).cte().alias('user_friends')

    mutual_friends = (
        select([curr_user_friends.c.friend_id.label('user_id')])
        .select_from(
            curr_user_friends.join(
                user_friends,
                curr_user_friends.c.friend_id == user_friends.c.friend_id
            )
        )
    ).cte().alias('mutual_friends')

    query = (
        select([
            user_table.c.user_id, user_table.c.first_name,
            user_table.c.last_name, user_table.c.description,
            user_table.c.profile_image_extension
        ])
        .select_from(
            user_table.join(
                mutual_friends,
                user_table.c.user_id == mutual_friends.c.user_id
            )
        )
        .order_by(user_table.c.first_name.asc())
        .order_by(user_table.c.last_name.asc())
        .limit(limit)
        .offset(offset)
    )

    users, error = None, None
    try:
        users = await db.fetch_all(query)
    except Exception as e:
        logging.error(e)
        error = e
    return {'users': users, 'error': error}


async def get_mutual_friend_count(
    db: Database,
    curr_user: Dict[str, str],
    user_id: str
):
    """
    Get the number of mutual friends between current user and input user
    """
    curr_user_id = curr_user["user_id"]
    curr_user_friends1 = (
        select([
            friendship_table.c.user_id1.label('friend_id')
        ])
        .select_from(friendship_table)
        .where((friendship_table.c.user_id2 == curr_user_id)
               & friendship_table.c.accepted_at.isnot(None))
    )
    curr_user_friends2 = (
        select([
            friendship_table.c.user_id2.label('friend_id')
        ])
        .select_from(friendship_table)
        .where((friendship_table.c.user_id1 == curr_user_id)
               & friendship_table.c.accepted_at.isnot(None))
    )
    curr_user_friends = union(
        curr_user_friends1, curr_user_friends2
    ).cte().alias('curr_user_friends')

    user_friends1 = (
        select([
            friendship_table.c.user_id1.label('friend_id')
        ])
        .select_from(friendship_table)
        .where((friendship_table.c.user_id2 == user_id)
               & friendship_table.c.accepted_at.isnot(None))
    )
    user_friends2 = (
        select([
            friendship_table.c.user_id2.label('friend_id')
        ])
        .select_from(friendship_table)
        .where((friendship_table.c.user_id1 == user_id)
               & friendship_table.c.accepted_at.isnot(None))
    )
    user_friends = union(
        user_friends1, user_friends2
    ).cte().alias('user_friends')

    mutual_friends = (
        select([curr_user_friends.c.friend_id.label('user_id')])
        .select_from(
            curr_user_friends.join(
                user_friends,
                curr_user_friends.c.friend_id == user_friends.c.friend_id
            )
        )
    ).cte().alias('mutual_friends')

    query = select([count()]).select_from(mutual_friends)

    mutual_friend_cnt, error = 0, None
    try:
        mutual_friend_cnt = await db.fetch_one(query)
    except Exception as e:
        logging.error(e)
        error = e
    return {'mutual_friend_count': mutual_friend_cnt, 'error': error}


# functions related to searching users from all users
async def search_user(
    db: Database,
    curr_user: Dict[str, str],
    search_option: str,  # email or name
    search_filter: str,
    limit: int = SEARCH_MAX_LIMIT,
    offset: int = 0
):
    assert search_option in ('email', 'name')

    user_id = curr_user["user_id"]

    search_filter = search_filter.lower()
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
        union(user_friends1, user_friends2).cte().alias('user_friends')
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
        .limit(limit)
    )

    users, error = None, None
    try:
        users = await db.fetch_all(query)
    except Exception as e:
        logging.error(e)
        error = e
    return {'users': users, 'error': error}
