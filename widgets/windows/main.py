from typing import Optional

import sqlalchemy
from PyQt5 import QtCore, QtWidgets, QtGui

from globals import config
from menus import GoToMenu, actions
from utils import monitors, window_watcher
from utils.event_logger import DBEventLogger
from web.backend import Server
from widgets import MainWidget
from widgets.tray import TrayWidget
from .help import HelpWindow
from .sess_manager_win import SessManagerWindow
from .web import WebWindow
from ..base import Base
from ..settings import SettingsWindow


class MainWindow(QtWidgets.QMainWindow, Base):
    def __init__(self, backend_server: Optional[Server], conn: sqlalchemy.engine.Connection, parent=None) -> None:
        super(MainWindow, self).__init__(parent)
        self.backend_server = backend_server

        # create window watcher
        self.threadpool = QtCore.QThreadPool()
        self.win_watcher = window_watcher.QtWindowWatcher()
        self.threadpool.start(self.win_watcher)

        # title
        self.setWindowTitle("Quick Task Switcher")

        # current flags
        self.flags = [
            QtCore.Qt.WindowStaysOnTopHint,  # always on top
            QtCore.Qt.Tool,  # this will hide the app from task bar and show it on all desktops
        ]
        self.set_flags()

        # semi-transparent
        self.setWindowOpacity(config.json_config.main_window_opacity)

        # central widget
        main_widget = MainWidget(self)
        self.setCentralWidget(main_widget)

        # other [helper] windows
        self.help_win = HelpWindow(self)
        self.web_win = WebWindow(self)
        self._sess_manager_win = None  # create on demand
        self._settings_win = None  # create on demand

        # context menu
        self.create_context_menu()

        # show
        self.show()

        # show/hide titlebar
        self.set_titlebar_state_from_config()

        # move to last known location if any
        if config.json_config.last_position is not None:
            # is location still in visible area?
            if monitors.is_loc_in_view(*config.json_config.last_position):
                self.move(*config.json_config.last_position)

        # TODO: workaround to remove extra space at top and bottom
        self.resize(100, 50)

        # system tray
        self.tray = TrayWidget(self)

        # create and start event logger
        self.db_logger = DBEventLogger(self, conn)
        self.db_logger.log_start()
        self.quit_logged = False  # TODO: workaround (see self.aboutToClose)

    @property
    def sess_manager_win(self) -> SessManagerWindow:
        if not self._sess_manager_win:
            self._sess_manager_win = SessManagerWindow(self)
        return self._sess_manager_win

    @property
    def settings_win(self) -> SettingsWindow:
        if not self._settings_win:
            self._settings_win = SettingsWindow(self)
        return self._settings_win

    def set_titlebar_state_from_config(self):
        if not config.json_config.titlebar_hidden:
            if QtCore.Qt.FramelessWindowHint in self.flags:
                self.flags.remove(QtCore.Qt.FramelessWindowHint)
        else:
            self.flags.append(QtCore.Qt.FramelessWindowHint)
        self.set_flags()
        self.show()

    def center(self):
        self.center_and_move()

    def set_flags(self):
        flags = 0
        for flag in self.flags:
            flags |= flag
        self.setWindowFlags(flags)

    def aboutToClose(self):
        # save position
        config.json_config.last_position = self.pos().x(), self.pos().y()

        # log quit event
        # TODO: workaround since this function is (for no apparent reason) called twice (at least) on quits
        if not self.quit_logged:
            self.quit_logged = True
            self.db_logger.log_quit()

    def closeEvent(self, event):
        config.quit_func()

    def keyPressEvent(self, event):
        # escape to close
        if event.key() == QtCore.Qt.Key_Escape:
            self.closeEvent(event)

        # ? to show help
        elif event.key() == QtCore.Qt.Key_Question:
            self.help_win.show()

        # T to toggle titlebar
        elif event.key() == QtCore.Qt.Key_T:
            config.json_config.titlebar_hidden = not config.json_config.titlebar_hidden
            self.set_titlebar_state_from_config()
            self.show()

        # M to minimize
        elif event.key() == QtCore.Qt.Key_M:
            self.hide()

        # D to open API docs
        elif event.key() == QtCore.Qt.Key_D:
            if self.backend_server is not None:
                self.backend_server.open_docs()
            else:
                QtWidgets.QMessageBox.critical(self, "Docs not available", "Backend server is not running!")

        # W to open web interface
        elif event.key() == QtCore.Qt.Key_W:
            self.web_win.reload_and_show()

        # S to open session manager
        elif event.key() == QtCore.Qt.Key_S:
            self.sess_manager_win.update_and_show()

        # Q to quit
        elif event.key() == QtCore.Qt.Key_Q:
            config.quit_func()

    def create_context_menu(self):
        self.menu = QtWidgets.QMenu(self)

        actions.add_change_desk_name_action(self.menu, self)
        actions.add_close_action(self.menu)

        goto_submenu = GoToMenu(parent=self.menu)
        self.menu.addMenu(goto_submenu)

        self.menu.addSeparator()
        actions.add_open_web_action(self.menu, self)
        self.menu.addSeparator()
        actions.add_sess_actions(self.menu, self)
        self.menu.addSeparator()
        actions.add_open_help_action(self.menu, self)
        actions.add_open_settings_action(self.menu, self)

        hide_action = self.menu.addAction('Minimize/Hide')
        hide_action.triggered.connect(self.hide)

        quit_action = self.menu.addAction("Quit")
        quit_action.triggered.connect(self.closeEvent)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        self.menu.exec_(self.mapToGlobal(event.pos()))
