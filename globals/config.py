import datetime
import threading
from dataclasses import dataclass, field
from typing import Tuple, List, Dict

from dataclasses_json import dataclass_json

from utils.stopwatch import StopWatch

config_lock = threading.Lock()


@dataclass_json
@dataclass
class JSONConfig:
    # configuration json file path
    config_path: str = 'config.json'

    # last screen position
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

    # main window opacity
    main_window_opacity: float = 0.8

    # grab area min width and height
    grab_area_min_size: Tuple[int, int] = (20, 10)

    # number of desktops
    # TODO: use this variable where appropriate instead of hard-coded values
    desktops_number: int = 9

    # quit time as unix timestamp in seconds
    quit_time: float = 0

    # prev session durations (maps desktop name to duration in milliseconds)
    prev_durations: Dict[str, float] = field(default_factory=lambda: {})

    # duration in seconds to identify new start as part of previous session
    # if new start is within this duration, user is asked to continue from previous session
    session_pause_dur: float = 4 * 60 * 60  # 4 hours

    # option to always continue from duration of previous session without asking
    always_cont_prev_dur: bool = False

    # path to sqlite database to log events
    db_path: str = 'qts.db'


class Config:
    # info about current desktop
    # initials: first desktop
    _curr_desk: int = 0
    _prev_curr_desk: int = 0

    @property
    def curr_desk(self):
        return self._curr_desk

    @curr_desk.setter
    def curr_desk(self, new_val: int):
        with config_lock:
            self._curr_desk = new_val

    @property
    def prev_curr_desk(self):
        return self._prev_curr_desk

    @prev_curr_desk.setter
    def prev_curr_desk(self, new_val: int):
        with config_lock:
            self._prev_curr_desk = new_val

    # info about total number of desktops
    # initials: one virtual desktop
    _desk_count: int = 1
    _prev_desk_count: int = 1

    @property
    def desk_count(self):
        return self._desk_count

    @desk_count.setter
    def desk_count(self, new_val: int):
        with config_lock:
            self._desk_count = new_val

    @property
    def prev_desk_count(self):
        return self._prev_desk_count

    @prev_desk_count.setter
    def prev_desk_count(self, new_val: int):
        with config_lock:
            self._prev_desk_count = new_val

    # desktops timers
    timers: List[StopWatch] = None

    # quit function (when app exists)
    quit_func = None

    # backend port
    backend_port: int = 56789

    # up time
    up_time: datetime.datetime = None

    # config save/loaded from json file
    json_config = JSONConfig()


config = Config()
