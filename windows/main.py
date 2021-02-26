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


class MainWindow(QtWidgets.QMainWindow):
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

    def set_titlebar_state_from_config(self):
        if not config.json_config.titlebar_hidden:
            if QtCore.Qt.FramelessWindowHint in self.flags:
                self.flags.remove(QtCore.Qt.FramelessWindowHint)
        else:
            self.flags.append(QtCore.Qt.FramelessWindowHint)
        self.set_flags()
        self.show()

    def center(self):
        first_monitor_center = monitors.get_in_view_loc()
        x = first_monitor_center[0] - self.size().width() / 2
        y = first_monitor_center[1] - self.size().height() / 2
        self.move(x, y)

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
        if event.key() == QtCore.Qt.Key_Question:
            self.help_win.show()

        # T to toggle titlebar
        if event.key() == QtCore.Qt.Key_T:
            config.json_config.titlebar_hidden = not config.json_config.titlebar_hidden
            self.set_titlebar_state_from_config()
            self.show()

        # M to minimize
        if event.key() == QtCore.Qt.Key_M:
            self.hide()

        # D to open API docs
        if event.key() == QtCore.Qt.Key_D:
            if self.backend_server is not None:
                self.backend_server.open_docs()
            else:
                QtWidgets.QMessageBox.critical(self, "Docs not available", "Backend server is not running!")

        # S to open session manager
        if event.key() == QtCore.Qt.Key_S:
            self.sess_manager_win.update_and_show()

        # Q to quit
        if event.key() == QtCore.Qt.Key_Q:
            config.quit_func()

    def create_context_menu(self):
        self.menu = QtWidgets.QMenu(self)

        actions.add_change_desk_name_action(self.menu, self)
        actions.add_close_action(self.menu)

        goto_submenu = GoToMenu(parent=self.menu)
        self.menu.addMenu(goto_submenu)

        self.menu.addSeparator()

        open_web = self.menu.addAction("Open analysis interface")
        open_web.triggered.connect(self.web_win.reload_and_show)

        self.menu.addSeparator()

        actions.add_sess_actions(self.menu, self)

        self.menu.addSeparator()

        hide_action = self.menu.addAction('Minimize/Hide')
        hide_action.triggered.connect(self.hide)

        quit_action = self.menu.addAction("Quit")
        quit_action.triggered.connect(self.closeEvent)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        self.menu.exec_(self.mapToGlobal(event.pos()))
