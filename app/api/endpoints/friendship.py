from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from starlette.config import Config
from starlette.status import (HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED,
                              HTTP_500_INTERNAL_SERVER_ERROR)
from databases import Database

from app.crud import crud_friendship, crud_user
from app.schemas.friendship import FriendshipRequest, FriendshipAccept, \
    FriendshipDelete, FriendshipInfo
from app.schemas.user import UserSummary
from app.api.deps import get_db
from app.api.auth.auth import get_current_user

config = Config(".env")

router = APIRouter()


@router.post("/request")
async def create_friendship_request(
    friendship_request: FriendshipRequest,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    user_id2 = friendship_request.dict()['user_id2']
    if curr_user['user_id'] == user_id2:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail=("User cannot send friend ",
                                    "request to oneself"))

    db_user2 = await crud_user.get_user_by_id(db, user_id2)
    if db_user2 is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,
                            detail="User not found")

    error = await crud_friendship.create_friendship_request(
        db, curr_user['user_id'], friendship_request
    )
    if error is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, there is something wrong")

    return {'success': True}


# get friendship requests that the current user has not accepted yet
@router.get("/request", response_model=FriendshipInfo)
async def get_friendship_requests(
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    res = await crud_friendship.get_friendship_requests(
        db, curr_user['user_id']
    )
    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    return res['request_arr']


@router.post("/delete")
async def delete_friendship_request(
    delete_request: FriendshipDelete,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user),
):
    if delete_request['user_id1'] is None:
        user_id1, user_id2 = curr_user['user_id'], delete_request['user_id2']
    elif delete_request['user_id2'] is None:
        user_id1, user_id2 = delete_request['user_id1'], curr_user['user_id']
    else:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail=("Invalid parameter: either user_id1 or ",
                                    "user_id2 must be None"))
    error = await crud_friendship.delete_friendship_request(
        db, user_id1, user_id2
    )
    if error is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return {'success': True}


@router.post("/accept")
async def accept_friendship_request(
    friendship_accept: FriendshipAccept,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    user_id1 = friendship_accept.dict()['user_id1']
    if curr_user['user_id'] == user_id1:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail=("User cannot accept friend ",
                                    "request to oneself"))

    db_user1 = await crud_user.get_user_by_id(user_id1)
    if db_user1 is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,
                            detail="User not found")

    error = await crud_friendship.accept_friendship_request(
        db, curr_user['user_id'], friendship_accept
    )
    if error is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")

    return {'success': True}


# search friends using email
@router.get("/search/email/{email}", response_model=List[UserSummary])
async def search_friends_by_email(
    email: str,
    exact: bool = False,
    limit: int = 10,
    offset: int = 0,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    if limit < 0 or offset < 0:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Limit and offset cannot be negative")
    if limit == 0:
        return []

    res = await crud_friendship.get_friends_by_email(
        db, curr_user['user_id'], email, exact, limit, offset=offset)
    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Sorry, something went wrong')

    return res['friends']


# search friends using name
@router.get("/search/name/{name}", response_model=List[UserSummary])
async def search_friends_by_name(
    name: str,
    exact: bool = False,
    limit: int = 10,
    offset: int = 0,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    if limit < 0 or offset < 0:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Limit and offset cannot be negative")
    if limit == 0:
        return []

    res = await crud_friendship.get_friends_by_name(
        db, curr_user['user_id'], name, exact, limit, offset=offset)
    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Sorry, something went wrong')
    return res['friends']
