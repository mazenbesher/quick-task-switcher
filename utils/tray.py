from PyQt5 import QtWidgets, QtGui

from globals import iconPaths, config
from utils import desk_info
from windows import MainWindow


def create() -> QtWidgets.QSystemTrayIcon:

    # create the tray
    tray = QtWidgets.QSystemTrayIcon()

    # change icon to current desk
    desk_info.update()
    tray.setIcon(QtGui.QIcon(iconPaths.desk(config.curr_desk)))
    tray.setVisible(True)

    return tray
