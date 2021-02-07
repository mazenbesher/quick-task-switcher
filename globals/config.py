from dataclasses import dataclass, field
from typing import Tuple, List

from PyQt5 import QtWidgets
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class JSONConfig:
    #
    config_path: str = 'config.json'

    #
    last_position: Tuple[int, int] = None

    # check desktop changes interval in msec
    check_interval: int = 1000

    # main window title bar status
    titlebar_hidden: bool = False

    # desk name char limit
    desk_name_char_limit: int = 50

    # desktop names
    desktop_names: List[str] = field(default_factory=lambda: [f'Desktop {i}' for i in range(1, 10)])

    # desktop name history
    desktop_names_history_max_size: int = 2
    desktop_names_history: List[str] = field(default_factory=lambda: [])


class Config:
    # info about current desktop
    desk_count: int = None
    prev_desk_count: int = None
    curr_desk: int = None  # 1-based index
    prev_curr_desk: int = None  # 1-based index

    #
    tray: QtWidgets.QSystemTrayIcon = None

    #
    quit_func = None

    #
    json_config = JSONConfig()


config = Config()
