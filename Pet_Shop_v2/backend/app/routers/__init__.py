from fastapi import APIRouter

from app.routers import admin, auth, live_pets, orders, pets, products, roles, users


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(admin.router)
api_router.include_router(products.router)
api_router.include_router(pets.router)
api_router.include_router(live_pets.router)
api_router.include_router(orders.router)

__all__ = ["api_router"]
