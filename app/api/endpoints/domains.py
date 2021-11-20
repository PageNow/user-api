from typing import Dict

from fastapi import APIRouter, Depends
from starlette.config import Config

from app.api.auth.auth import get_current_user

config = Config(".env")

router = APIRouter()


@router.get("/share/warnings")
async def get_domain_share_warnings(
    curr_user: Dict[str, str] = Depends(get_current_user)
):
    warnings = {
        'google.com': (
            'Allowing google.com may result in sharing personal activities '
            '(e.g. Gmail, Calendar)'
        ),
        'messenger.com': (
            'Allowing messenger.com may result in sharing personal activities'
        ),
        'notion.so': (
            'Allowing notion.so may result in sharing personal activities'
        )
    }
    return warnings
