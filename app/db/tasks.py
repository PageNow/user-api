from fastapi import FastAPI
from databases import Database

from app.core.config import DATABASE_URL, DATABASE_RO_URL
from app.core.logger import logging


async def connect_to_db(app: FastAPI) -> None:
    logging.info(f'Connecting to database: {DATABASE_URL}')
    database = Database(DATABASE_URL, min_size=2, max_size=10)

    try:
        await database.connect()
        app.state._db = database
        logging.info('Database connected')
    except Exception as e:
        logging.error('***** DB CONNECTION ERRORR *****')
        logging.error(e)
        print(e)
        logging.error("***** DB CONNECTION ERROR *****")


async def connect_to_db_ro(app: FastAPI) -> None:
    logging.info(f'Connecting to database: {DATABASE_RO_URL}')
    database_ro = Database(DATABASE_RO_URL, min_size=2, max_size=10)

    try:
        await database_ro.connect()
        app.state._db_ro = database_ro
        logging.info('Database_ro connected')
    except Exception as e:
        logging.error('*** DB_RO CONNECTION ERRORR ***')
        logging.error(e)
        print(e)
        logging.error("*** DB_RO CONNECTION ERROR ***")


async def close_db_connection(app: FastAPI) -> None:
    try:
        await app.state._db.disconnect()
    except Exception as e:
        logging.error("*** DB DISCONNECTION ERROR ***")
        logging.error(e)
        logging.error("*** DB DISCONNECTION ERROR ***")
