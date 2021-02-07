import sys

from PyQt5 import QtWidgets

from windows import MainWindow
from utils import tray
from globals import config


def main():
    app = QtWidgets.QApplication(sys.argv)

    # system tray
    config.tray = tray.create()

    # add the menu to the tray
    config.tray_menu = QtWidgets.QMenu()
    config.tray.setContextMenu(config.tray_menu)

    # add quit action to system tray
    quit = QtWidgets.QAction("Quit")
    quit.triggered.connect(app.quit)
    config.tray_menu.addAction(quit)

    # main window
    main_window = MainWindow()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
