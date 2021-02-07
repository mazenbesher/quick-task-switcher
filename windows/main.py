from PyQt5 import QtCore, QtWidgets

from globals import config
from widgets import MainWidget
from .help import HelpWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None) -> None:
        super(MainWindow, self).__init__(parent)

        # size
        self.setFixedSize(175, 35)

        # title
        self.setWindowTitle("Quick Task Switcher")

        # title bar status
        self.titlebar_hidden = False

        # current flags
        self.flags = [
            QtCore.Qt.WindowStaysOnTopHint,  # always on top
            QtCore.Qt.Tool,  # this will hide the app from task bar and show it on all desktops
        ]
        self.set_flags()

        # semi-transparent
        self.setWindowOpacity(0.8)

        # central widget
        main_widget = MainWidget(self)
        self.setCentralWidget(main_widget)

        # help window
        self.help_win = HelpWindow(self)

        # show
        self.show()

        # move to last known location if any
        if config.json_config.last_position is not None:
            self.move(*config.json_config.last_position)

    def set_flags(self):
        flags = 0
        for flag in self.flags:
            flags |= flag
        self.setWindowFlags(flags)

    def closeEvent(self, event):
        # save position
        config.json_config.last_position = self.pos().x(), self.pos().y()

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
            if self.titlebar_hidden:
                self.flags.remove(QtCore.Qt.FramelessWindowHint)
                self.titlebar_hidden = False
            else:
                self.flags.append(QtCore.Qt.FramelessWindowHint)
                self.titlebar_hidden = True
            self.set_flags()
            self.show()
