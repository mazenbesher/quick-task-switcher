import io

from fastapi import APIRouter
from mss import mss, tools
from starlette.responses import StreamingResponse

router = APIRouter(tags=['Screenshots', 'Desktops'])


@router.get('/', summary='Generate a screenshot of current desktop')
async def screenshot():
    with mss() as sct:
        mon_idx: int = 0  # 0 => all monitors
        mon = sct.monitors[mon_idx]
        sct_img = sct.grab(mon)
        sct_img_bytes = tools.to_png(sct_img.rgb, sct_img.size)
        return StreamingResponse(io.BytesIO(sct_img_bytes), media_type="image/png")
