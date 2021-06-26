import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from databases import Database

from app.crud import crud_user
from app.schemas.user import UserPublic, UserPrivate, UserCreate
from app.api.deps import get_db
from app.api.auth.auth import get_current_user

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

@router.get("/me", response_model=UserPrivate)
async def get_user_private(
    db: Database = Depends(get_db), username: str = Depends(get_current_user)
):
    db_user = await crud_user.get_user_by_id(username)
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="User not found")
    return db_user

@router.get("/{user_uuid}", response_model=UserPublic)
async def get_user_public(user_uuid: uuid.UUID, db: Database = Depends(get_db)):
    db_user = await crud_user.get_user_by_uuid(db, user_uuid)
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="User not found")
    output = dict(db_user)
    if not output['dob_public']:
        output['dob'] = None
    return output
