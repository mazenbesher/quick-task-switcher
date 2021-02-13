from fastapi import APIRouter

from globals import config
from .desktops_info import router as desktops_info_router

router = APIRouter(tags=['Info'])
router.include_router(desktops_info_router, prefix='/desktops')


@router.get('/uptime', summary='Get up time (since script start)')
async def uptime() -> float:
    return config.up_time.timestamp()
