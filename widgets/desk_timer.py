from PyQt5 import QtWidgets, QtCore

from globals import config, signals
from utils.stopwatch import StopWatch


class DeskTimerLabel(QtWidgets.QLabel):
    def __init__(self, parent):
        super(DeskTimerLabel, self).__init__(parent)

        # timer for each desktop
        assert config.timers is None
        config.timers = []
        for desk_idx in range(config.json_config.desktops_number):
            desk_name = config.json_config.desktop_names[desk_idx]
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
        signals.currDeskChanged.connect(self.desktopChanged)
        signals.deskClosed.connect(self.deskClosed)

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
