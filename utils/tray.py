from PyQt5 import QtWidgets, QtGui

from globals import iconPaths, config
from utils import desk_info


def create() -> QtWidgets.QSystemTrayIcon:
    # create the icon
    icon = QtGui.QIcon(iconPaths.start)

    # create the tray
    tray = QtWidgets.QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    # change icon to current desk
    desk_info.update()
    tray.setIcon(QtGui.QIcon(iconPaths.desk(config.currDesk)))

    return tray
