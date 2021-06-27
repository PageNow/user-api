import uuid
from typing import Dict

from sqlalchemy.sql.expression import literal_column
from databases import Database

from app.models.user import user_table
from app.schemas.user import UserCreate

async def get_user_by_id(db: Database, user_id: str):
    query = user_table.select().where(user_table.c.user_id == user_id)
    user = await db.fetch_one(query)
    return user

async def get_user_by_uuid(db: Database, user_uuid: uuid.UUID):
    query = user_table.select().where(user_table.c.user_uuid == user_uuid)
    user = await db.fetch_one(query)
    return user

async def create_user(db: Database, curr_user: Dict[str, str], user: UserCreate):
    user_dict = user.dict()
    user_dict.update(curr_user)
    query = user_table.insert().values(**user_dict)
    error = None
    try:
        await db.execute(query)
    except Exception as e:
        error = e
    return error
