import datetime
import enum
import uuid
from pathlib import Path
from typing import Dict

import sqlalchemy as sql
from PyQt5 import QtCore

from globals import signals, config
from utils import desk_manager


class AppEvents(enum.Enum):
    Start = enum.auto()
    Quit = enum.auto()


class DBEventLogger(QtCore.QObject):
    """
    Note: to log start and quit events, log_* must be called manually
    """

    def __init__(self, parent, db_path: Path):
        super(DBEventLogger, self).__init__(parent)

        # unique id for each session
        self.session_id: str = str(uuid.uuid4())

        # connect
        engine: sql.engine.Engine = sql.create_engine(
            'sqlite:///' + db_path.resolve().as_posix(),
            echo=True  # enable logging
        )
        self.conn = engine.connect()
        metadata = sql.MetaData()

        # make sure to start once
        self.started = False

        # don't update prev row of fg_win_change table if first call to log_fg_win_change or log_quit
        self.first_fg_win = True

        # foreground window change table and signals
        self.fg_win_change_table = sql.Table(
            'fg_win_change', metadata,
            sql.Column('id', sql.Integer, primary_key=True),
            sql.Column('desk', sql.String),
            sql.Column('proc', sql.String),
            sql.Column('title', sql.String),
            sql.Column('pinned_win', sql.Boolean),
            sql.Column('pinned_app', sql.Boolean),
            sql.Column('sess_id', sql.String, default=lambda: self.session_id),
            sql.Column('time_utc', sql.DateTime, default=datetime.datetime.utcnow),

            # durations are updated when next row is inserted or app closed
            sql.Column('duration_seconds', sql.Integer, default=-1),
            sql.Column('duration_microseconds', sql.Integer, default=-1),
        )
        signals.foreground_window_changed.connect(self.log_fg_win_change)

        # app events (start,quit) table
        # Note: to log start and quit events, log_* must be called manually
        self.app_events_table = sql.Table(
            'app_events', metadata,
            sql.Column('event', sql.Enum(AppEvents)),
            sql.Column('desk', sql.String),
            sql.Column('sess_id', sql.String, default=lambda: self.session_id),
            sql.Column('time_utc', sql.DateTime, default=datetime.datetime.utcnow),
        )

        # desk change events table and signals
        self.desk_changes_table = sql.Table(
            'desk_changes', metadata,
            sql.Column('desk', sql.String),
            sql.Column('sess_id', sql.String, default=lambda: self.session_id),
            sql.Column('time_utc', sql.DateTime, default=datetime.datetime.utcnow),
        )
        signals.curr_desk_changed.connect(self.log_desk_changed)
        signals.curr_desk_name_changed.connect(self.log_desk_changed)

        # session durations table
        self.sess_dur_table = sql.Table(
            'sess_dur', metadata,
            sql.Column('sess_id', sql.String, primary_key=True, default=lambda: self.session_id),
            sql.Column('desk_dur_sec_json', sql.JSON),
            sql.Column('time_utc', sql.DateTime, default=datetime.datetime.utcnow),
        )

        # create tables
        metadata.create_all(engine)

        # delete records older than json_config.db_delete_older_than_days (https://stackoverflow.com/a/15881195/1617883)
        # TODO: add delete if size bigger than x
        if config.json_config.db_delete_older_than_days != -1:
            too_old = datetime.datetime.utcnow() - datetime.timedelta(
                days=config.json_config.db_delete_older_than_days
            )
            for table in metadata.tables:
                self.conn.execute(table.delete().where(table.c.time_utc <= too_old))

    def _record_session_durations(self) -> Dict[str, int]:
        """
        Insert or update corresponding record in database
        :return: inserted desk durations (key: desk name, val: duration in seconds)
        """

        # get first desk name and time in this session from app_events table
        query = sql.sql.select([
            self.app_events_table.c.desk,
            self.app_events_table.c.time_utc,
        ]).where(self.app_events_table.c.sess_id == self.session_id)
        res = self.conn.execute(query).fetchone()
        curr_desk: str = res.values()[0]
        curr_time: datetime.datetime = res.values()[1]

        # get all desk change events in current session
        query = sql.sql.select([self.desk_changes_table]).where(self.desk_changes_table.c.sess_id == self.session_id)
        desk_dur: Dict[str, datetime.timedelta] = {}
        for row in self.conn.execute(query).fetchall():
            new_desk, time_utc = row['desk'], row['time_utc']
            if curr_desk in desk_dur:
                desk_dur[curr_desk] += (time_utc - curr_time)
            else:
                desk_dur[curr_desk] = time_utc - curr_time
            curr_time, curr_desk = time_utc, new_desk

        # add last
        assert curr_desk == config.json_config.desktop_names[config.curr_desk]
        last_time = datetime.datetime.utcnow()
        if curr_desk in desk_dur:
            desk_dur[curr_desk] += (last_time - curr_time)
        else:
            desk_dur[curr_desk] = last_time - curr_time

        # jsonify and store in db (update if already recorded)
        desk_dur_sec_json: Dict[str, int] = {k: v.seconds for k, v in desk_dur.items()}
        sess_already_exists = self.conn.execute(
            self.sess_dur_table.select().where(self.sess_dur_table.c.sess_id == self.session_id)
        ).scalar() is not None

        if not sess_already_exists:
            self.conn.execute(self.sess_dur_table.insert().values(
                desk_dur_sec_json=desk_dur_sec_json
            ))
        else:
            # update existing row
            self.conn.execute(self.sess_dur_table.update().where(
                self.sess_dur_table.c.sess_id == self.session_id
            ).values(
                desk_dur_sec_json=desk_dur_sec_json
            ))

        return desk_dur_sec_json

    def log_start(self):
        if self.started:
            raise ValueError('Already started!')

        self.started = True
        ins = self.app_events_table.insert().values(
            event=AppEvents.Start,
            desk=config.json_config.desktop_names[config.curr_desk],
        )
        self.conn.execute(ins)

    def log_quit(self):
        self._record_session_durations()

        if not self.started:
            raise ValueError('Not started!')

        if not self.first_fg_win:
            self._set_last_fg_win_duration_from_now()

        ins = self.app_events_table.insert().values(
            event=AppEvents.Quit,
            desk=config.json_config.desktop_names[config.curr_desk],
        )
        self.conn.execute(ins)

    def get_session_durations(self) -> Dict[str, int]:
        """
        :return: desk durations (key: desk name, val: duration in seconds)
        """
        return self._record_session_durations()

    @QtCore.pyqtSlot()
    def log_desk_changed(self):
        ins = self.desk_changes_table.insert().values(
            desk=config.json_config.desktop_names[config.curr_desk],
        )
        self.conn.execute(ins)

    def _set_last_fg_win_duration_from_now(self):
        # get last row
        query = (sql.sql
                 .select([self.fg_win_change_table.c.time_utc, self.fg_win_change_table.c.id])
                 .order_by(sql.desc('time_utc')))
        last_row: sql.engine.RowProxy = self.conn.execute(query).first()
        last_row_id: int = last_row.values()[1]

        # get last time_utc (i.e. when the latest fg win was activated)
        app_start_time_utc: datetime.datetime = last_row.values()[0]

        # update duration by using current time
        delta = datetime.datetime.utcnow() - app_start_time_utc
        duration_seconds = delta.seconds
        duration_microseconds = delta.microseconds
        query = (self.fg_win_change_table
                 .update()
                 .where(self.fg_win_change_table.c.id == last_row_id)
                 .values(duration_seconds=duration_seconds, duration_microseconds=duration_microseconds))
        self.conn.execute(query)

    @QtCore.pyqtSlot(int)
    def log_fg_win_change(self, hwnd: int):
        if not self.first_fg_win:
            self._set_last_fg_win_duration_from_now()
        self.first_fg_win = False

        window = desk_manager.get_hwnd_window(hwnd)
        ins = self.fg_win_change_table.insert().values(
            proc=window.proc_name,
            title=window.title,
            desk=config.json_config.desktop_names[config.curr_desk],
            pinned_app=window.is_pinned_app,
            pinned_win=window.is_pinned_win,
        )
        self.conn.execute(ins)

    @staticmethod
    def _process_like_term(search_term: str) -> str:
        """
        Allow "known" wildcards in search term and produce compatible term for SQL
        Known -> SQL    Desc
        _     -> __     skips underscore
        *     -> %      matches any sequence of zero or more characters.
        ?     -> _      matches any single character

        References:
            - https://www.sqlitetutorial.net/sqlite-like/
            - https://stackoverflow.com/a/12060886/1617883
        """
        if '*' in search_term or '_' in search_term:
            return search_term.replace('_', '__').replace('*', '%').replace('?', '_')
        return f'%{search_term}%'

    def get_proc_fg(self, proc: str, fro: datetime.datetime) -> sql.engine.ResultProxy:
        """
        The results has the following useful methods:
            fetchall: retrieve all data as list of tuples
            keys:     columns names

        Example: convert results to pandas dataframe (https://stackoverflow.com/a/12060886/1617883)
        ```python
        res = db_event_logger.get_proc_fg('firefox', dt)
        df = pd.DataFrame(res.fetchall())
        df.columns = res.keys()
        ```
        """
        return self.conn.execute(
            sql.sql.select([
                self.fg_win_change_table.c.desk,
                self.fg_win_change_table.c.title,
                self.fg_win_change_table.c.pinned_win,
                self.fg_win_change_table.c.pinned_app,
                self.fg_win_change_table.c.time_utc,
            ]).where(sql.and_(
                self.fg_win_change_table.c.proc == proc,
                self.fg_win_change_table.c.time_utc > fro
            ))
        )

    def get_proc_fg_like(self, proc_search_term: str, fro: datetime.datetime) -> sql.engine.ResultProxy:
        """
        This method is similar to `get_proc_fg` but uses ilike (case INsensitive) for searching instead of exact
        match
        https://stackoverflow.com/a/4926793/1617883
        """
        proc_search_term = self._process_like_term(proc_search_term)
        return self.conn.execute(
            sql.sql.select([
                self.fg_win_change_table.c.desk,
                self.fg_win_change_table.c.title,
                self.fg_win_change_table.c.pinned_win,
                self.fg_win_change_table.c.pinned_app,
                self.fg_win_change_table.c.time_utc,
            ]).where(sql.and_(
                self.fg_win_change_table.c.proc.ilike(proc_search_term),
                self.fg_win_change_table.c.time_utc > fro,
            ))
        )

    def get_proc_desk_fg_like(self, proc_search_term: str, desk: str, fro: datetime.datetime) -> sql.engine.ResultProxy:
        proc_search_term = self._process_like_term(proc_search_term)
        return self.conn.execute(
            sql.sql.select([
                self.fg_win_change_table.c.title,
                self.fg_win_change_table.c.pinned_win,
                self.fg_win_change_table.c.pinned_app,
                self.fg_win_change_table.c.time_utc,
            ]).where(sql.and_(
                self.fg_win_change_table.c.proc.ilike(proc_search_term),
                self.fg_win_change_table.c.desk == desk,
                self.fg_win_change_table.c.time_utc > fro,
            ))
        )
