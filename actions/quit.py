from PyQt5 import QtWidgets

from globals import config


def create_quit_action(app: QtWidgets.QApplication) -> QtWidgets.QAction:
    quit_action = QtWidgets.QAction("Quit")
    quit_action.triggered.connect(config.quit_func)
    return quit_action
