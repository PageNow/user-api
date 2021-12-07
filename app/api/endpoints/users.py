from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict, List
import logging
import asyncio
import functools

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import (HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND,
                              HTTP_500_INTERNAL_SERVER_ERROR)
from starlette.config import Config
from databases import Database
import boto3
from botocore.exceptions import ClientError

from app.crud import crud_user, crud_friendship
from app.schemas.user import UserPublic, UserPrivate, UserBase,\
    UserSummary, UserUpdate
from app.api.deps import get_db, get_executor, get_s3_client
from app.api.auth.auth import get_current_user
from app.utils.helpers import convert_to_user_info_public

config = Config(".env")
PROFILE_IMAGE_BUCKET_NAME = config("PROFILE_IMAGE_BUCKET_NAME", cast=str)

router = APIRouter()


@router.post("/me", response_model=UserPrivate)
async def create_user(
    user: UserBase,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    db_user = await crud_user.get_user_by_id(db, curr_user['user_id'])
    if db_user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="User already exists")
    error = await crud_user.create_user(db, curr_user, user)
    if error is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")

    db_user = await crud_user.get_user_by_id(db, curr_user['user_id'])
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="User not found")
    return db_user


@router.put("/me", response_model=UserPrivate)
async def update_user(
    user: UserUpdate,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    db_user = await crud_user.get_user_by_id(db, curr_user['user_id'])
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="User not found")
    error = await crud_user.update_user(db, curr_user, user)
    if error is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=error)

    user_info = await crud_user.get_user_by_id(db, curr_user['user_id'])
    return user_info


@router.put("/me/domain_array/{share_type}", response_model=UserPrivate)
async def update_user_domain_allow_array(
    domain_array: List[str],
    share_type: str,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    if share_type not in ('allow', 'deny'):
        return HTTPException(status_code=HTTP_400_BAD_REQUEST,
                             detail="share_type must be 'allow' or 'deny'")

    db_user = await crud_user.get_user_by_id(db, curr_user['user_id'])
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="User not found")

    error = await crud_user.update_domain_array(db, curr_user, domain_array,
                                                share_type)
    if error is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=error)

    user_info = await crud_user.get_user_by_id(db, curr_user['user_id'])
    return user_info


@router.get("/me", response_model=UserPrivate)
async def get_user_private(
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    db_user = await crud_user.get_user_by_id(db, curr_user['user_id'])
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="User not found")
    return db_user


@router.get("/id/{user_id}", response_model=UserPublic)
async def get_user_public(
    user_id: str,
    db: Database = Depends(get_db)
):
    db_user = await crud_user.get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="User not found")

    return convert_to_user_info_public(db_user)


@router.get("/ids/{user_id_arr}", response_model=List[UserPublic])
async def get_users_public(
    user_id_arr: str,
    db: Database = Depends(get_db)
):
    user_id_arr = user_id_arr.split(',')
    db_user_arr = await crud_user.get_users_by_id(db, user_id_arr)
    db_user_arr = list(
        map(lambda x: convert_to_user_info_public(x), db_user_arr)
    )

    return db_user_arr


@router.get("/id/{user_id}/mutual-friends", response_model=List[UserSummary])
async def get_user_mutual_friends(
    user_id: str,
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

    res = await crud_user.get_mutual_friends(
        db, curr_user, user_id, limit=limit, offset=offset
    )
    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return res['users']


@router.get("/id/{user_id}/mutual-friends/count")
async def get_user_mutual_friend_count(
    user_id: str,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    res = await crud_user.get_mutual_friend_count(
        db, curr_user, user_id
    )
    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return res['mutual_friend_count']


@router.get("/id/{user_id}/friends")
async def get_user_friends(
    user_id: str,
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

    res = await crud_friendship.get_user_friends_with_friendship_state(
        db, user_id, curr_user['user_id'], limit=limit, offset=offset
    )
    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return res['friends']


@router.get("/id/{user_id}/friends/count")
async def get_user_friend_count(
    user_id: str,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    res = await crud_friendship.get_user_friend_count(db, user_id)
    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return res['friend_count']


# TODO: accept other file types
@router.get("/me/profile-image-upload-url")
async def get_user_profile_image_upload_url(
    image_ext: str,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user),
    s3_client: boto3.client = Depends(get_s3_client),
    executor: ThreadPoolExecutor = Depends(get_executor)
):
    """ Get a presigned url to upload profile image to s3 """
    db_user = await crud_user.get_user_by_id(db, curr_user['user_id'])
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="User not found")
    try:
        loop = asyncio.get_running_loop()
        url = await loop.run_in_executor(
            executor,
            functools.partial(
                s3_client.generate_presigned_url,
                'put_object',
                Params={
                    'Bucket': PROFILE_IMAGE_BUCKET_NAME,
                    'Key': f'{db_user["user_id"]}/profile_image.{image_ext}',
                    'ACL': 'private',
                    'ContentType': f'image/{image_ext}',
                },
                ExpiresIn=60 * 60,
                HttpMethod='PUT'
            )
        )
    except ClientError as e:
        logging.error(e)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=e)

    error = await crud_user.update_profile_upload_time(
        db, curr_user['user_id'], image_ext)
    if error is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=error)

    return url


# assumes user_id exists
@router.get("/id/{user_id}/profile-image-url")
async def get_user_profile_image_url(
    image_ext: str,
    user_id: str,
    s3_client: boto3.client = Depends(get_s3_client),
    executor: ThreadPoolExecutor = Depends(get_executor)
):
    """ Get a presigned url to get the profile image of a user from s3 """
    try:
        loop = asyncio.get_running_loop()
        url = await loop.run_in_executor(
            executor,
            functools.partial(
                s3_client.generate_presigned_url,
                'get_object',
                Params={
                    'Bucket': PROFILE_IMAGE_BUCKET_NAME,
                    'Key': f'{user_id}/profile_image.{image_ext}'
                },
                ExpiresIn=60 * 60,
                HttpMethod='GET'
            )
        )
    except ClientError as e:
        logging.error(e)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=e)
    return url


@router.get("/ids/{user_id_arr}/profile-image-url")
async def get_users_profile_image_url_arr(
    image_ext_arr: str,
    user_id_arr: str,
    s3_client: boto3.client = Depends(get_s3_client),
    executor: ThreadPoolExecutor = Depends(get_executor)
):
    image_ext_arr = image_ext_arr.split(',')
    user_id_arr = user_id_arr.split(',')
    if len(image_ext_arr) != len(user_id_arr):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Invalid parameters and query")

    try:
        tasks = []
        loop = asyncio.get_running_loop()
        for idx in range(len(user_id_arr)):
            params = {
                'Bucket': PROFILE_IMAGE_BUCKET_NAME,
                'Key': f'{user_id_arr[idx]}/profile_image.{image_ext_arr[idx]}'
            }
            tasks.append(
                loop.run_in_executor(
                    executor,
                    functools.partial(
                        s3_client.generate_presigned_url,
                        'get_object',
                        Params=params,
                        ExpiresIn=60 * 60,  # expires in
                        HttpMethod='GET'
                    )
                )
            )
        url_arr = await asyncio.gather(*tasks)
        url_dict = dict()
        for idx in range(len(user_id_arr)):
            url_dict[user_id_arr[idx]] = url_arr[idx]

    except ClientError as e:
        logging.error(e)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=e)

    return url_dict


@router.delete("/me/profile-image")
async def delete_user_profile_image(
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user),
    s3_client: boto3.client = Depends(get_s3_client)
):
    db_user = await crud_user.get_user_by_id(db, curr_user['user_id'])
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="User not found")
    error = None
    try:
        s3_client.delete_object(
            Bucket=PROFILE_IMAGE_BUCKET_NAME,
            Key=f'{db_user["user_id"]}/profile_image.png'
        )
        error = await crud_user.delete_profile_image_info(
            db, curr_user['user_id'])
    except ClientError as e:
        logging.error(e)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=e)

    if error is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=error)

    return {'success': True}
