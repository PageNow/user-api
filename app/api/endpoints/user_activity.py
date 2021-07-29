from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from starlette.config import Config
from databases import Database
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.crud import crud_user_activity
from app.schemas.user_url_history import UserUrlHistory, UserUrlHistorySave
from app.api.deps import get_db
from app.api.auth.auth import get_current_user

config = Config(".env")

router = APIRouter()


@router.post("/me/url-history", response=UserUrlHistory)
async def save_url_history(
    user_url_history: UserUrlHistorySave,
    db: Database = Depends(get_db),
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    error = await crud_user_activity.save_user_url_history(
        db, curr_user['user_id'], user_url_history
    )
    if error is not None:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Sorry, something went wrong")
    return {'success': True}
