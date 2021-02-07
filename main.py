import sys

from PyQt5 import QtWidgets

from globals import config
from utils import tray, config_manager
from windows import MainWindow


def main():
    # load config
    config_manager.load_json_config()

    # create app
    app = QtWidgets.QApplication(sys.argv)

    # set style sheet
    with open('assets/style.css') as fp:
        app.setStyleSheet(fp.read())

    # main window
    main_window = MainWindow()

    # quit function
    def quit_func():
        main_window.aboutToClose()
        config_manager.save_json_config()
        app.quit()

    config.quit_func = quit_func

    # system tray
    config.tray = tray.create()

    # add the menu to the tray
    tray_menu = QtWidgets.QMenu()
    config.tray.setContextMenu(tray_menu)

    # add center main window action
    center_main_win_action = QtWidgets.QAction("Center Window")
    center_main_win_action.triggered.connect(main_window.center)
    tray_menu.addAction(center_main_win_action)

    # add quit action to system tray
    quit_action = QtWidgets.QAction("Quit")
    quit_action.triggered.connect(config.quit_func)
    tray_menu.addAction(quit_action)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
