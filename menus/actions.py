import keyboard
from PyQt5 import QtWidgets

from globals import config
from utils import dialogs


def add_change_desk_name_action(menu: QtWidgets.QMenu, parent: QtWidgets.QWidget):
    rename_action = menu.addAction("Rename current desktop")
    rename_action.triggered.connect(lambda: dialogs.change_curr_desk_name(parent))


def add_close_action(menu: QtWidgets.QMenu):
    close_action = menu.addAction("Close current desktop")
    close_action.triggered.connect(lambda: keyboard.press_and_release('ctrl+win+f4'))


def add_sess_actions(menu: QtWidgets.QMenu, main_window: 'MainWindow'):
    save_sess = menu.addAction("Save session")
    save_sess.triggered.connect(config.session_manager.save_current_sess)

    load_sess = menu.addAction("Load session")
    load_sess.triggered.connect(config.session_manager.load_latest_sess)

    open_sess_manager = menu.addAction("Open session manager")
    open_sess_manager.triggered.connect(main_window.sess_manager_win.update_and_show)


def add_open_help_action(menu: QtWidgets.QMenu, main_window: 'MainWindow'):
    help_action = menu.addAction('Help')
    help_action.triggered.connect(main_window.help_win.show)


def add_open_web_action(menu: QtWidgets.QMenu, main_window: 'MainWindow'):
    open_web = menu.addAction("Open analysis interface")
    open_web.triggered.connect(main_window.web_win.reload_and_show)
