import datetime
import enum
from pathlib import Path

import sqlalchemy as sql
from PyQt5 import QtCore

from globals import signals, config
from utils import window_watcher, desk_manager, desk_watcher


class AppEvents(enum.Enum):
    Start = enum.auto()
    Quit = enum.auto()


class DeskEvents(enum.Enum):
    Changed = enum.auto()
    Closed = enum.auto()
    Renamed = enum.auto()
    New = enum.auto()


class DBEventLogger(QtCore.QObject):
    """
    Note: to log start and quit events, log_* must be called manually
    """

    def __init__(self, parent, db_path: Path):
        super(DBEventLogger, self).__init__(parent)

        # connect
        engine: sql.engine.Engine = sql.create_engine(
            'sqlite:///' + db_path.resolve().as_posix(),
            echo=True  # enable logging
        )
        self.conn = engine.connect()
        metadata = sql.MetaData()

        # TODO: delete records older than x (https://stackoverflow.com/a/15881195/1617883)

        # foreground window change table and signals
        self.fg_win_change_table = sql.Table(
            'fg_win_change', metadata,
            sql.Column('desk', sql.String),
            sql.Column('proc', sql.String),
            sql.Column('title', sql.String),
            sql.Column('pinned_win', sql.Boolean),
            sql.Column('pinned_app', sql.Boolean),
            sql.Column('time_utc', sql.DateTime, default=datetime.datetime.utcnow),
            # https://stackoverflow.com/a/13370382/1617883
        )
        signals.foreground_window_changed.connect(self.log_fg_win_change)

        # app events (start,quit) table
        # Note: to log start and quit events, log_* must be called manually
        self.app_events_table = sql.Table(
            'app_events', metadata,
            sql.Column('event', sql.Enum(AppEvents)),
            sql.Column('time_utc', sql.DateTime, default=datetime.datetime.utcnow),
        )

        # desk events table and signals
        self.desk_events_table = sql.Table(
            'desk_events', metadata,
            sql.Column('event', sql.Enum(DeskEvents)),
            sql.Column('prev_val', sql.String),
            sql.Column('new_val', sql.String),
            sql.Column('time_utc', sql.DateTime, default=datetime.datetime.utcnow),
        )
        signals.desk_closed.connect(self.log_desk_closed)
        signals.new_desk.connect(self.log_new_desk)
        signals.curr_desk_changed.connect(self.log_desk_changed)
        signals.curr_desk_name_changed.connect(self.log_desk_name_changed)

        # create tables
        metadata.create_all(engine)

    def log_start(self):
        ins = self.app_events_table.insert().values(
            event=AppEvents.Start
        )
        self.conn.execute(ins)

    def log_quit(self):
        ins = self.app_events_table.insert().values(
            event=AppEvents.Quit
        )
        self.conn.execute(ins)

    @QtCore.pyqtSlot()
    def log_desk_name_changed(self):
        ins = self.desk_events_table.insert().values(
            event=DeskEvents.Renamed,
            new_val=config.json_config.desktop_names[config.curr_desk],
        )
        self.conn.execute(ins)

    @QtCore.pyqtSlot()
    def log_desk_changed(self):
        # TODO: skip event at program start
        ins = self.desk_events_table.insert().values(
            event=DeskEvents.Changed,
            prev_val=config.prev_curr_desk,
            new_val=config.curr_desk,
        )
        self.conn.execute(ins)

    @QtCore.pyqtSlot()
    def log_new_desk(self):
        # TODO: skip event at program start
        ins = self.desk_events_table.insert().values(
            event=DeskEvents.New,
            new_val=config.json_config.desktop_names[config.curr_desk],
        )
        self.conn.execute(ins)

    @QtCore.pyqtSlot()
    def log_desk_closed(self):
        ins = self.desk_events_table.insert().values(
            event=DeskEvents.Closed,
            new_val=config.json_config.desktop_names[config.curr_desk],
        )
        self.conn.execute(ins)

    @QtCore.pyqtSlot(int)
    def log_fg_win_change(self, hwnd: int):
        window = desk_manager.get_hwnd_window(hwnd)
        ins = self.fg_win_change_table.insert().values(
            proc=window.proc_name,
            title=window.title,
            desk=config.json_config.desktop_names[config.curr_desk],
            pinned_app=window.is_pinned_app,
            pinned_win=window.is_pinned_win
        )
        self.conn.execute(ins)


if __name__ == '__main__':
    import sys

    from PyQt5 import QtWidgets, QtCore


    class MainWidget(QtWidgets.QWidget):
        def __init__(self, parent):
            super(MainWidget, self).__init__(parent)

            layout = QtWidgets.QVBoxLayout()

            self.label = QtWidgets.QLabel('Hello World')
            self.label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(self.label)

            self.btn = QtWidgets.QPushButton('Press me')
            self.btn.clicked.connect(self.btn_clicked)
            layout.addWidget(self.btn)

            self.setLayout(layout)

        @QtCore.pyqtSlot()
        def btn_clicked(self):
            self.label.setText('Pressed!!!')


    class MainWin(QtWidgets.QMainWindow):
        def __init__(self, parent=None):
            super(MainWin, self).__init__(parent)

            self.db_logger = DBEventLogger(self, db_path=Path('example.db'))

            # window change watcher
            self.threadpool = QtCore.QThreadPool()
            self.win_watcher = window_watcher.QtWindowWatcher()
            self.threadpool.start(self.win_watcher)

            # desk change watcher
            self.curr = desk_manager.get_curr_desktop_number()
            self.count = desk_manager.get_desktop_count()

            self.timer = desk_watcher.DesktopWatcherQt()
            self.timer.signals.desk_changed.connect(self.desk_changed)
            self.timer.signals.desk_count_changed.connect(self.count_changed)

            self.setCentralWidget(MainWidget(self))
            self.show()

        @QtCore.pyqtSlot()
        def desk_changed(self):
            new = desk_manager.get_curr_desktop_number()
            print(f'desk changed from {self.curr} to {new}')
            self.curr = new

        @QtCore.pyqtSlot()
        def count_changed(self):
            new = desk_manager.get_desktop_count()
            print(f'count changed from {self.count} to {new}')
            self.count = new


    def main():
        app = QtWidgets.QApplication(sys.argv)

        main_window = MainWin()

        sys.exit(app.exec_())


    main()
