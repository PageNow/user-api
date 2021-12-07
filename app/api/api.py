from fastapi import APIRouter

from app.api.endpoints import users, friendship, \
    user_search, core, domains, share_notifications

api_router = APIRouter()

api_router.include_router(
    users.router, prefix='/users', tags=["users"]
)

api_router.include_router(
    friendship.router, prefix='/friendship', tags=["friendship"]
)

api_router.include_router(
    user_search.router, prefix='/users/search', tags=['user-search']
)

api_router.include_router(
    domains.router, prefix='/domains', tags=['domains']
)

api_router.include_router(
    share_notifications.router, prefix='/notifications/share',
    tags=['share-notifications']
)

api_router.include_router(
    core.router, prefix='', tags=['core']
)
