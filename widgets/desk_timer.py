from PyQt5 import QtWidgets, QtCore

from globals import config, signals
from utils.stopwatch import StopWatch


class DeskTimerLabel(QtWidgets.QLabel):
    def __init__(self, parent):
        super(DeskTimerLabel, self).__init__(parent)

        # timer for each desktop
        self.timers = []
        for desk_idx in range(config.desk_count):
            desk_name = config.json_config.desktop_names[desk_idx]
            watch = StopWatch(desk_name)
            if desk_idx == config.curr_desk - 1:
                # start watch on current desktop
                watch.start()
            self.timers.append(watch)

        # set name (for css ref for instance)
        self.setObjectName("DeskTimerLabel")

        # set initial text
        self.updateText()

        # show
        self.show()

        # connect signals
        signals.currDeskChanged.connect(self.desktopChanged)
        signals.newDesk.connect(self.newDesk)
        signals.deskClosed.connect(self.deskClosed)

        # refresh timer text each second
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.updateText)
        self.timer.start()

    @QtCore.pyqtSlot()
    def desktopChanged(self):
        # if not moving from closed desktop
        if config.prev_curr_desk is not None and \
                config.prev_curr_desk - 1 < len(self.timers) and \
                self.timers[config.prev_curr_desk - 1].running:
            # pause prev desktop watch
            self.timers[config.prev_curr_desk - 1].pause()

        # resume new desktop watch
        self.timers[config.curr_desk - 1].start()

        # show
        self.updateText()

    @QtCore.pyqtSlot()
    def newDesk(self):
        # add new watch for the new desktop
        # Note: new desktops are always add at the end
        self.timers.append(StopWatch())

    @QtCore.pyqtSlot()
    def deskClosed(self):
        # remove closed desktop watch
        closed_desk_id = config.curr_desk - 1
        print(f'closed_desk_id: {closed_desk_id}')
        del self.timers[closed_desk_id]

    def updateText(self):
        self.setText(self.timers[config.curr_desk - 1].get_elapsed_formatted())
