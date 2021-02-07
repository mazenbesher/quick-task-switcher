from PyQt5 import QtWidgets


class Config:
    deskCount: int = None
    currDesk: int = None
    tray: QtWidgets.QSystemTrayIcon = None
    tray_menu: QtWidgets.QMenu = None


config = Config()
