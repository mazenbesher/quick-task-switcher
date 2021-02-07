import sys

from PyQt5 import QtWidgets

from windows import MainWindow
from utils import tray, config_manager
from globals import config
import actions


def main():
    # load config
    config_manager.load_json_config()

    # create app
    app = QtWidgets.QApplication(sys.argv)

    # quit function
    def quit_func():
        config_manager.save_json_config()
        app.quit()

    # system tray
    config.tray = tray.create()

    # add the menu to the tray
    config.tray_menu = QtWidgets.QMenu()
    config.tray.setContextMenu(config.tray_menu)

    # add quit action to system tray
    config.quit_func = quit_func
    config.quit_action = actions.create_quit_action(app)
    config.tray_menu.addAction(config.quit_action)

    # main window
    main_window = MainWindow()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
