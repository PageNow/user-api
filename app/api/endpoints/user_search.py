from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from starlette.config import Config
from starlette.status import HTTP_400_BAD_REQUEST, \
    HTTP_500_INTERNAL_SERVER_ERROR
from databases import Database

from app.api.deps import get_db
from app.api.auth.auth import get_current_user
from app.crud import crud_user
from app.schemas.user import UserSummary

config = Config(".env")

router = APIRouter()


@router.get("/email/{email}", response_model=List[UserSummary])
async def search_users_by_email(
    email: str,
    limit: int = 15,
    offset: int = 0,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    if limit < 0 or offset < 0:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Limit and offset cannot be negative")
    if limit == 0:
        return []

    email = email.strip('\\')

    res = await crud_user.search_user(
        db, curr_user, 'email', email, limit=limit, offset=offset)
    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return res['users']


@router.get("/name/{name}", response_model=List[UserSummary])
async def search_users_by_name(
    name: str,
    limit: int = 15,
    offset: int = 0,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user),
):
    if limit < 0 or offset < 0:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Limit and offset cannot be negative")
    if limit == 0:
        return []

    name = name.strip('\\')

    res = await crud_user.search_user(
        db, curr_user, 'name', name, limit=limit, offset=offset)
    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return res['users']
