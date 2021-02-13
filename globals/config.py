from dataclasses import dataclass, field
from typing import Tuple, List

from PyQt5 import QtWidgets
from dataclasses_json import dataclass_json

from utils.stopwatch import StopWatch


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
    titlebar_hidden: bool = True

    # desk name char limit
    desk_name_char_limit: int = 50

    # desktop names
    desktop_names: List[str] = field(default_factory=lambda: [f'Desktop {i}' for i in range(1, 10)])

    # desktop name history
    desktop_names_history_max_size: int = 20
    desktop_names_history: List[str] = field(default_factory=lambda: [])

    #
    main_window_opacity: float = 0.8

    # grab area min width and height
    grab_area_min_size: Tuple[int, int] = (20, 10)

    # number of desktops
    # TODO: use this variable where appropriate instead of hard-coded values
    desktops_number: int = 9


class Config:
    # info about current desktop
    # initials: first desktop
    curr_desk: int = 0
    prev_curr_desk: int = 0

    # info about total number of desktops
    # initials: one virtual desktop
    desk_count: int = 1
    prev_desk_count: int = 1

    # desktops timers
    timers: List[StopWatch] = None

    #
    tray: QtWidgets.QSystemTrayIcon = None

    #
    quit_func = None

    # backend port
    backend_port: int = 56789

    #
    json_config = JSONConfig()


config = Config()
