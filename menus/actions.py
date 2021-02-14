import keyboard
from PyQt5 import QtWidgets

from utils import dialogs


def add_change_desk_name_action(menu: QtWidgets.QMenu, parent: QtWidgets.QWidget):
    rename_action = menu.addAction("Rename current desktop")
    rename_action.triggered.connect(lambda: dialogs.change_curr_desk_name(parent))


def add_close_action(menu: QtWidgets.QMenu):
    close_action = menu.addAction("Close current desktop")
    close_action.triggered.connect(lambda: keyboard.press_and_release('ctrl+win+f4'))
