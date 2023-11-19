from fastapi import APIRouter

# from .account import router as account_router
# from .auth import router as auth_router
from .index_ import router as index__router
from .daily_log import router as daily_log_router
from .exercise_category import router as exercise_category_router
from .performance_log import router as performance_log_router

API_ROUTERS: list[APIRouter] = [
    # account_router,
    # auth_router,
    daily_log_router,
    exercise_category_router,
    performance_log_router,
    index__router,
]
