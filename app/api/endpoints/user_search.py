from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette.config import Config
from starlette.status import HTTP_400_BAD_REQUEST, \
    HTTP_500_INTERNAL_SERVER_ERROR
from databases import Database

from app.api.deps import get_db
from app.crud import crud_user
from app.schemas.user import UserSummary

config = Config(".env")

router = APIRouter()


@router.get("/email/{email}", response_model=List[UserSummary])
async def search_users_by_email(
    email: str,
    exact: bool = False,
    limit: int = 10,
    offset: int = 0,
    db: Database = Depends(get_db),
):
    if limit < 0 or offset < 0:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Limit and offset cannot be negative")
    if limit == 0:
        return []

    res = await crud_user.search_user_by_email(
        db, email, exact, limit, offset=offset)
    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return res['users']


@router.get("/name/{name}", response_model=List[UserSummary])
async def search_users_by_name(
    name: str,
    exact: bool = False,
    limit: int = 10,
    offset: int = 0,
    db: Database = Depends(get_db),
):
    if limit < 0 or offset < 0:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Limit and offset cannot be negative")
    if limit == 0:
        return []

    res = await crud_user.search_user_by_name(
        db, name, exact, limit, offset=offset)
    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return res['users']
