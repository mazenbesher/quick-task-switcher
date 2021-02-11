from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from globals import config

router = APIRouter()


class DesktopInfo(BaseModel):
    name: str
    num: int
    duration_seconds: int


@router.get('/', summary='Info about current open desktops', response_model=List[DesktopInfo])
async def desktops_info():
    result = []
    for desk_idx in range(config.desk_count):
        result.append(DesktopInfo(
            name=config.json_config.desktop_names[desk_idx],
            num=desk_idx + 1,
            duration_seconds=config.timers[desk_idx].get_elapsed(),
        ))
    return result
