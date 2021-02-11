import sys

from PyQt5 import QtWidgets

from globals import config
from utils import config_manager
from utils.paths import resource_path
from web import backend
from widgets.tray import TrayWidget
from windows import MainWindow


def main():
    # start backend server
    server = backend.Server()
    server.run_in_thread()

    # load config
    config_manager.load_json_config()

    # create app
    app = QtWidgets.QApplication(sys.argv)

    # set style sheet
    with open(resource_path('assets/style.css')) as fp:
        app.setStyleSheet(fp.read())

    # main window
    main_window = MainWindow(backend_server=server)

    # quit function
    def quit_func():
        # stop backend server
        server.stop()

        # notify main window about close
        main_window.aboutToClose()

        # save config
        config_manager.save_json_config()

        # quit qt app
        app.quit()

    config.quit_func = quit_func

    # system tray
    config.tray = TrayWidget(main_window)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
