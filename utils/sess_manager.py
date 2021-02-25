"""
Save/Load sessions
A session is the open windows and their corresponding desktop (reference by name not number!)
"""
import datetime
from dataclasses import dataclass
from typing import List

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from dataclasses_json import dataclass_json

from globals import config
from utils import desk_manager


@dataclass_json
@dataclass
class SavedSessionWindow:
    window: desk_manager.Window
    desk_name: str


@dataclass_json
@dataclass
class Session:
    windows: List[SavedSessionWindow]


class SessionManager:
    def __init__(self, conn: sqlalchemy.engine.Connection):
        self.conn = conn
        metadata = sqlalchemy.MetaData()

        # create sessions table
        self.sess_table = sqlalchemy.Table(
            'sessions', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('sess', sqlalchemy.String),
            sqlalchemy.Column('time_utc', sqlalchemy.DateTime, default=datetime.datetime.utcnow),
        )
        metadata.create_all(self.conn.engine)

    def save_current_sess(self):
        self.conn.execute(self.sess_table.insert().values(
            sess=Session(
                windows=[
                    SavedSessionWindow(
                        window=win,
                        desk_name=config.json_config.desktop_names[win.desk_num]
                    )
                    for win in desk_manager.get_windows_on_all_desk()
                ]
            ).to_json()
        ))

    def load_latest_sess(self):
        self.load(self.get_last_sess())

    def get_last_sess(self) -> Session:
        # TODO: if no last session => warning

        windows_json = self.conn.execute(sqlalchemy.sql.select([
            self.sess_table.c.sess
        ]).order_by(self.sess_table.c.time_utc.desc())).first()[0]
        return Session.from_json(windows_json)

    @staticmethod
    def load(sess: Session):
        for win in desk_manager.get_windows_on_all_desk():
            for saved_win in sess.windows:
                if win.title == saved_win.window.title and saved_win.desk_name in config.json_config.desktop_names:
                    desk_num = config.json_config.desktop_names.index(saved_win.desk_name)
                    desk_manager.move_window_to_desktop(win.hwnd, desk_num)
