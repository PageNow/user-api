import uuid

from fastapi import APIRouter, Depends, HTTPException
from databases import Database

from app.crud import crud_user
from app.schemas.user import User, UserCreate
from app.api.deps import get_db

router = APIRouter()


@router.post("/me")
async def create_user(user: UserCreate, db: Database = Depends(get_db)):
    db_user = await crud_user.get_user_by_id(db, user.user_id)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    error = await crud_user.create_user(db, user)
    if error is not None:
        return {'success': False, 'error': error}
    return {'success': True, 'error': None}

@router.get("/{user_uuid}", response_model=User,
          response_model_exclude_unset=True)
async def get_user_public(user_uuid: uuid.UUID, db: Database = Depends(get_db)):
    db_user = await crud_user.get_user_by_uuid(db, user_uuid)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
