from fastapi import APIRouter

from .account import router as account_router
from .auth import router as auth_router
from .index_ import router as index__router

API_ROUTERS: list[APIRouter] = [
    account_router,
    auth_router,
    index__router,
]
