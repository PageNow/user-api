import os

from fastapi import FastAPI
from databases import Database

from app.core.config import DATABASE_URL, POSTGRES_SERVER
from app.core.logger import logging


async def connect_to_db(app: FastAPI) -> None:
    logging.info(f'Connecting to database: {DATABASE_URL}')
    if POSTGRES_SERVER == 'localhost' or os.environ.get("TESTING"):
        is_ssl = False
    else:
        is_ssl = True

    if os.environ.get("TESTING"):
        db_url = f"{DATABASE_URL}_test"
    else:
        db_url = DATABASE_URL
    database = Database(db_url, min_size=2, max_size=10, ssl=is_ssl)

    try:
        await database.connect()
        app.state._db = database
        logging.info('Database connected')
    except Exception as e:
        logging.error('***** DB CONNECTION ERRORR *****')
        logging.error(e)
        print(e)
        logging.error("***** DB CONNECTION ERROR *****")


async def close_db_connection(app: FastAPI) -> None:
    try:
        await app.state._db.disconnect()
    except Exception as e:
        logging.error("*** DB DISCONNECTION ERROR ***")
        logging.error(e)
        logging.error("*** DB DISCONNECTION ERROR ***")
