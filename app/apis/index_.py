import logging

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.sql import expression as sa_exp

from app.ctx import AppCtx

logger = logging.getLogger(__name__)

router = APIRouter()


class PingGetResponse(BaseModel):
    okay: bool


@router.get("/_ping", response_model=PingGetResponse)
async def _() -> PingGetResponse:
    try:
        if (await AppCtx.current.db.session.scalar(sa_exp.select(1))) != 1:
            raise RuntimeError("DB healthcheck is failed : unexpected response")
    except Exception:
        logger.warning("Failed to complete ping", exc_info=True)
        return PingGetResponse(okay=False)
    else:
        return PingGetResponse(okay=True)
