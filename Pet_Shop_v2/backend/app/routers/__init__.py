from fastapi import APIRouter

from app.routers import admin, auth, roles, users


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(admin.router)

__all__ = ["api_router"]
