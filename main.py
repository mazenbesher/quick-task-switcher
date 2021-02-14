import datetime
import sys

from PyQt5 import QtWidgets, QtCore

from globals import config
from utils import config_manager, desk_watcher, desk_info
from utils.paths import resource_path
from web import backend
from widgets.tray import TrayWidget
from windows import MainWindow


def main():
    # record up time
    config.up_time = datetime.datetime.now()

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

    # setup desk change watcher (timer as fallback)
    try:
        timer = desk_watcher.DesktopWatcherQt()
        timer.signals.desk_changed.connect(desk_info.update)
        timer.signals.desk_count_changed.connect(desk_info.update)
    except desk_watcher.RegKeysNotExist:
        # timer fallback
        QtWidgets.QMessageBox.warning(main_window, "Warning", "Can not register registry callbacks")

        # refresh desk info each check_interval
        timer = QtCore.QTimer()
        timer.setInterval(config.json_config.check_interval)
        timer.timeout.connect(desk_info.update)
        timer.start()

    # quit function
    def quit_func():
        # stop desk watcher
        timer.stop()  # Note timer can be desk_watcher.DesktopWatcherQt or QtCore.QTimer

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
    TrayWidget(main_window)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
