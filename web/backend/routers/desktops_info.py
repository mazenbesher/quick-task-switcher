from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from globals import config

router = APIRouter(tags=['Info', 'Desktops'])


class DesktopInfo(BaseModel):
    name: str
    num: int
    duration_seconds: int


@router.get('/', summary='Info about all currently opened desktops', response_model=List[DesktopInfo])
async def desktops_info() -> List[DesktopInfo]:
    return [DesktopInfo(
        name=config.json_config.desktop_names[desk_idx],
        num=desk_idx + 1,
        duration_seconds=config.timers[desk_idx].get_elapsed(),
    ) for desk_idx in range(config.desk_count)]


@router.get('/{desk_id}', summary='Info about a specific opened desktop', response_model=DesktopInfo)
async def desktop_info(desk_id: int) -> DesktopInfo:
    if desk_id < 0 or desk_id >= config.desk_count:
        raise HTTPException(status_code=404, detail=f'Desktop with id {desk_id} does not exist')

    return DesktopInfo(
        name=config.json_config.desktop_names[desk_id],
        num=desk_id + 1,
        duration_seconds=config.timers[desk_id].get_elapsed(),
    )
