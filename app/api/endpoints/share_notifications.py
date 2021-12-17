from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from starlette.config import Config
from starlette.status import (HTTP_500_INTERNAL_SERVER_ERROR)
from databases import Database

from app.crud import crud_share_notification
from app.api.deps import get_db
from app.api.auth.auth import get_current_user
from app.schemas.share_notification import ShareNotificationCreate, \
    ShareNotificationRead, ShareNotificationsSent

config = Config(".env")

router = APIRouter()


@router.get("")
async def get_share_notifications_received(
    is_read: bool = None,  # if None, get all notifications,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    if is_read is None:
        res = await crud_share_notification.get_all_sharing_notifications(
            db, curr_user['user_id']
        )
    else:
        res = await crud_share_notification.get_sharing_notifications(
            db, curr_user['user_id'], is_read
        )

    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return res['notifications']


@router.get("/sent", response_model=List[ShareNotificationsSent])
async def get_share_notifications_sent(
    limit: int = 10,
    offset: int = 0,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    res = await crud_share_notification.get_sharing_notifications_sent(
        db, curr_user['user_id'], limit, offset
    )

    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return res['notifications_sent']


@router.post("")
async def create_share_notification(
    share_notification: ShareNotificationCreate,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    res = await crud_share_notification.create_sharing_notification(
        db, curr_user['user_id'], share_notification
    )

    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return res['event_id']


@router.post("/personal")
async def create_personal_share_notification(
    share_notification: ShareNotificationCreate,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    res = await crud_share_notification.create_personal_sharing_notification(
        db, curr_user['user_id'], share_notification
    )

    if res['error'] is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return res['event_id']


@router.post("/read")
async def read_share_notifications(
    share_notification_read: List[ShareNotificationRead],
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    error = await crud_share_notification.read_sharing_notification(
        db, curr_user['user_id'], share_notification_read
    )
    if error is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return {'success': True}
