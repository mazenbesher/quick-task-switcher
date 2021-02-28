from PyQt5 import QtWidgets

from widgets.base import Base


class SettingsWindow(QtWidgets.QMainWindow, Base):

    def __init__(self, parent):
        super(SettingsWindow, self).__init__(parent)

        # title
        self.setWindowTitle("Settings")

        self.tab_widget = QtWidgets.QTabWidget()
        # self.tab_widget.addTab(GlobalShortcutsTab(self), 'Global Shortcuts')

        self.setCentralWidget(self.tab_widget)

        self.adjustSize()
        self.center_and_move()
