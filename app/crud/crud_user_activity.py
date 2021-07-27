import datetime
import logging

from databases import Database

from app.models.user_url_history import user_url_history_table
from app.schemas.user_url_history import UserUrlHistorySave


async def save_user_url_history(
    db: Database,
    curr_user_id: str,
    user_url_history: UserUrlHistorySave
):
    user_url_history_dict = user_url_history.dict()
    user_url_history_dict.update({
        'user_id': curr_user_id,
        'accessed_at': datetime.datetime.utcnow()
    })
    query = user_url_history_table.insert().values(**user_url_history_dict)
    error = None
    try:
        await db.execute(query)
    except Exception as e:
        logging.error(e)
        error = e
    return error
