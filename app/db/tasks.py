import logging

from fastapi import FastAPI
from databases import Database

from app.core.config import DATABASE_URL

logger = logging.getLogger(__name__)


async def connect_to_db(app: FastAPI) -> None:
    database = Database(DATABASE_URL, min_size=2, max_size=10)

    try:
        await database.connect()
        app.state._db = database
    except Exception as e:
        logger.warn('*** DB CONNECTION ERRORR ***')
        logger.warn(e)
        logger.warn("*** DB CONNECTION ERROR ***")


async def close_db_connection(app: FastAPI) -> None:
    try:
        await app.state._db.disconnect()
    except Exception as e:
        logger.warn("*** DB DISCONNECTION ERROR ***")
        logger.warn(e)
        logger.warn("*** DB DISCONNECTION ERROR ***")
