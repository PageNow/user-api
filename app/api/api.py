from fastapi import APIRouter

from app.api.endpoints import users
from app.api.endpoints import friendship

api_router = APIRouter()

api_router.include_router(
    users.router, prefix="/users", tags=["users"]
)

api_router.include_router(
    friendship.router, prefix="/friendship", tags=["friendship"]
)
