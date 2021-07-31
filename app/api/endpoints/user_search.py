from fastapi import APIRouter, Depends, HTTPException
from starlette.config import Config
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from databases import Database

from app.api.deps import get_db
from app.crud import crud_user

config = Config(".env")

router = APIRouter()


@router.get("/name/{name}")
async def search_users_by_name(
    name: str,
    exact: bool = False,
    limit: int = 10,
    offset: int = 0,
    db: Database = Depends(get_db)
):
    users = await crud_user.search_user_by_name(
        db, name, exact, limit, offset=offset)
    if users is None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return users


@router.get("/email/{email}")
async def search_users_by_email(
    email: str,
    exact: bool = False,
    limit: int = 10,
    offset: int = 0,
    db: Database = Depends(get_db)
):
    users = await crud_user.search_user_by_email(
        db, email, exact, limit, offset=offset)
    if users is None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return users
