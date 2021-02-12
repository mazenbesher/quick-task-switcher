from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import desktops_info, screenshot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(desktops_info.router, prefix="/desktops_info")
app.include_router(screenshot.router, prefix="/screenshot")
