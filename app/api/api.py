from fastapi import APIRouter

from app.api.endpoints import users, friendship, user_activity, user_search

api_router = APIRouter()

api_router.include_router(
    users.router, prefix='/users', tags=["users"]
)

api_router.include_router(
    user_activity.router, prefix='/user-activity', tags=['user-activity']
)

api_router.include_router(
    friendship.router, prefix='/friendship', tags=["friendship"]
)

api_router.include_router(
    user_search.router, prefix='/user-search', tags=['search']
)
