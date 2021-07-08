import uuid
from typing import Dict
import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from starlette.config import Config
from databases import Database
import boto3
from botocore.exceptions import ClientError

from app.crud import crud_user
from app.schemas.user import UserPublic, UserPrivate, UserCreate, UserUpdate
from app.api.deps import get_db, get_s3_client
from app.api.auth.auth import get_current_user

config = Config(".env")
PROFILE_IMAGE_BUCKET_NAME = config("PROFILE_IMAGE_BUCKET_NAME", cast=str)

router = APIRouter()


@router.post("/me")
async def create_user(
    user: UserCreate,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    db_user = await crud_user.get_user_by_id(db, curr_user['user_id'])
    if db_user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User already exists")
    error = await crud_user.create_user(db, curr_user, user)
    if error is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=error)
    return {'success': True, 'error': None}

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

@router.get("/me/profile-image-upload-url")
async def get_user_profile_image_upload_url(
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user),
    s3_client: boto3.client = Depends(get_s3_client)
):
    """ Get a presigned url to upload profile image to s3 """
    db_user = await crud_user.get_user_by_id(db, curr_user['user_id'])
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="User not found")
    
    try:
        url = s3_client.generate_presigned_url('put_object',
            Params={
                'Bucket': PROFILE_IMAGE_BUCKET_NAME,
                'Key': f'{db_user["user_uuid"]}/profile_image.png',
                'ACL': 'private',
                'ContentType': 'image/png',
            },
            ExpiresIn=60 * 60,
            HttpMethod='PUT'
        )
    except ClientError as e:
        logging.error(e)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=e)

    error = await crud_user.update_profile_upload_time(
        db, curr_user['user_id'])
    if error is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=error)

    return {'data': url}

@router.get("/{user_uuid}", response_model=UserPublic)
async def get_user_public(
    user_uuid: uuid.UUID,
    db: Database = Depends(get_db)
):
    db_user = await crud_user.get_user_by_uuid(db, user_uuid)
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="User not found")
    output = dict(db_user)
    if not output['dob_public']:
        output['dob'] = None
    if not output['gender_public']:
        output['gender'] = None
    if not output['school_public']:
        output['school'] = None
    if not output['work_public']:
        output['work'] = None
    if not  output['location_public']:
        output['location'] = None
    return output

# assumes user_uuid exists
@router.get("/{user_uuid}/profile-image-url")
async def get_user_profile_image_url(
    user_uuid: uuid.UUID,
    db: Database = Depends(get_db),
    s3_client: boto3.client = Depends(get_s3_client)
):
    """ Get a presigned url to get the profile image of a user from s3 """
    try:
        url = s3_client.generate_presigned_url('get_object',
            Params={
                'Bucket': PROFILE_IMAGE_BUCKET_NAME,
                'Key': f'{user_uuid}/profile_image.png',
                # 'ACL': 'private',
                # 'ContentType': 'image/png',
            },
            ExpiresIn=60 * 60,
            HttpMethod='GET'
        )
    except ClientError as e:
        logging.error(e)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=e)
    return {'data': url}