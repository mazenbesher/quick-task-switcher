from dataclasses import dataclass
from typing import Tuple

from dataclasses_json import dataclass_json

from PyQt5 import QtWidgets


@dataclass_json
@dataclass
class JSONConfig:
    #
    config_path: str = 'config.json'

    #
    last_position: Tuple[int, int] = None


class Config:
    # info about current desktop
    deskCount: int = None
    currDesk: int = None

    #
    tray: QtWidgets.QSystemTrayIcon = None
    tray_menu: QtWidgets.QMenu = None

    #
    quit_func = None
    quit_action = None

    #
    json_config = JSONConfig()


config = Config()
