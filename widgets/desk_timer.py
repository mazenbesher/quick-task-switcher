import datetime

from PyQt5 import QtWidgets, QtCore

from globals import config, signals, messages
from utils.stopwatch import StopWatch


class DeskTimerLabel(QtWidgets.QLabel):
    def __init__(self, parent):
        super(DeskTimerLabel, self).__init__(parent)

        # option to load prev session durations if in the same day into current timers
        load_prev_durations = False
        if len(config.json_config.prev_durations.keys()) > 0:
            # is within the same session?
            now = datetime.datetime.now()
            prev_quit_time = datetime.datetime.fromtimestamp(config.json_config.quit_time)

            if (now - prev_quit_time).seconds <= config.json_config.session_pause_dur:
                # user confirmation
                if config.json_config.always_cont_prev_dur:
                    response = QtWidgets.QMessageBox.Yes

                    # inform user
                    # TODO: this should be done preferably via toast message (tray.showMessage) and
                    # must check in advance if system supports this (tray.isSystemTrayAvailable)
                    # and only use QMessageBox as fallback.
                    # More info: https://doc.qt.io/qt-5/qsystemtrayicon.html
                    # This, however, can not be done now since the tray is initialized AFTER the main window which
                    # initializes this widget, but the tray needs the main window as parent! (i.e. circular dependency)
                    QtWidgets.QMessageBox.information(self, *messages.load_prev_durations_info())
                else:
                    # ask
                    response = QtWidgets.QMessageBox.question(self, *messages.load_prev_durations_question())

                # set flag
                if response == QtWidgets.QMessageBox.Yes:
                    load_prev_durations = True

        # timer for each desktop
        assert config.timers is None
        config.timers = []
        for desk_idx in range(config.json_config.desktops_number):
            desk_name = config.json_config.desktop_names[desk_idx]

            if load_prev_durations and desk_name in config.json_config.prev_durations:
                watch = StopWatch(desk_name, start_seconds=config.json_config.prev_durations[desk_name])
            else:
                watch = StopWatch(desk_name)

            if desk_idx == config.curr_desk:
                # start watch on current desktop
                watch.start()
            config.timers.append(watch)

        # set name (for css ref for instance)
        self.setObjectName("DeskTimerLabel")

        # set initial text
        self.updateText()

        # show
        self.show()

        # connect signals
        signals.curr_desk_changed.connect(self.desktopChanged)
        signals.desk_closed.connect(self.deskClosed)

        # refresh timer text each second
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.updateText)
        self.timer.start()

    @QtCore.pyqtSlot()
    def deskClosed(self):
        closed_desk_id = config.curr_desk
        if config.timers[closed_desk_id].running:
            config.timers[closed_desk_id].pause()
        config.timers[closed_desk_id].reset()

    @QtCore.pyqtSlot()
    def desktopChanged(self):
        # if not moving from closed desktop
        if config.prev_curr_desk is not None and \
                config.prev_curr_desk < len(config.timers) and \
                config.timers[config.prev_curr_desk].running:
            # pause prev desktop watch
            print(f'Pausing desktop {config.prev_curr_desk + 1}')
            config.timers[config.prev_curr_desk].pause()

        # resume new desktop watch
        if not config.timers[config.curr_desk].running:
            print(f'Resuming desktop {config.curr_desk + 1}')
            config.timers[config.curr_desk].start()

        # show
        self.updateText()

    def updateText(self):
        self.setText(config.timers[config.curr_desk].get_elapsed_formatted())
