from PyQt5 import QtCore, QtWidgets, QtGui

from globals import config
from menus import GoToMenu
from widgets import MainWidget
from widgets.desk_name import DeskNameLabel
from .help import HelpWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None) -> None:
        super(MainWindow, self).__init__(parent)

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

        # help window
        self.help_win = HelpWindow(self)

        # show
        self.show()

        # show/hide titlebar
        self.set_titlebar_state_from_config()

        # move to last known location if any
        if config.json_config.last_position is not None:
            self.move(*config.json_config.last_position)

        # TODO: workaround to remove extra space at top and bottom
        self.resize(100, 50)

    def set_titlebar_state_from_config(self):
        if not config.json_config.titlebar_hidden:
            if QtCore.Qt.FramelessWindowHint in self.flags:
                self.flags.remove(QtCore.Qt.FramelessWindowHint)
        else:
            self.flags.append(QtCore.Qt.FramelessWindowHint)
        self.set_flags()
        self.show()

    def center(self):
        # TODO: hard coded coordinates!
        self.move(300, 300)

    def set_flags(self):
        flags = 0
        for flag in self.flags:
            flags |= flag
        self.setWindowFlags(flags)

    def aboutToClose(self):
        # save position
        config.json_config.last_position = self.pos().x(), self.pos().y()

    def closeEvent(self, event):
        self.aboutToClose()
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

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        menu = QtWidgets.QMenu(self)

        rename_action = menu.addAction("Rename current desktop")
        rename_action.triggered.connect(self.findChild(DeskNameLabel).changeCurrDeskName)

        goto_submenu = GoToMenu(parent=menu)
        menu.addMenu(goto_submenu)

        hide_action = menu.addAction('Minimize/Hide')
        hide_action.triggered.connect(self.hide)

        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.closeEvent)

        menu.exec_(self.mapToGlobal(event.pos()))
