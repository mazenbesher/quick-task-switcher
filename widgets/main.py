from PyQt5 import QtCore, QtWidgets, QtGui

from globals import config, signals
from utils import desk_info, desk_manager
from .desk_name import DeskNameLabel
from .desk_num_key import DeskNumKeysWidget
from .desk_timer import DeskTimerLabel
from .grab_area_widget import GrabAreaWidget


class MainWidget(QtWidgets.QWidget):

    def __init__(self, parent):  # , grabButton: QtCore.Qt.MouseButton = QtCore.Qt.LeftButton):
        super(MainWidget, self).__init__(parent)
        # self.grabButton = grabButton

        # set name (for css ref for instance)
        self.setObjectName("MainWidget")

        # TODO: enable only via a flag
        # TODO: automate this in a loop
        signals.deskClosed.connect(self.signalsDebugFn('deskClosed'))
        signals.newDesk.connect(self.signalsDebugFn('newDesk'))
        signals.currDeskChanged.connect(self.signalsDebugFn('currDeskChanged'))
        signals.currDeskNameChanged.connect(self.signalsDebugFn('currDeskNameChanged'))

        # layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(layout)

        # widgets
        layout.addWidget(DeskNumKeysWidget(self))

        # desk name and timer on the same line
        sublayout = QtWidgets.QHBoxLayout()
        sublayout.addWidget(DeskNameLabel(self), alignment=QtCore.Qt.AlignLeft)
        sublayout.addWidget(GrabAreaWidget(self), alignment=QtCore.Qt.AlignCenter)
        sublayout.addWidget(DeskTimerLabel(self), alignment=QtCore.Qt.AlignRight)
        sublayout.setSpacing(0)
        sublayout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(sublayout)

        # refresh desk info each check_interval
        self.timer = QtCore.QTimer()
        self.timer.setInterval(config.json_config.check_interval)
        self.timer.timeout.connect(desk_info.update)
        self.timer.start()

    def signalsDebugFn(self, event_name: str):
        def fn():
            msg = event_name
            msg += f'\n\tCount: {config.desk_count}, Prev Count: {config.prev_desk_count}'
            msg += f'\n\tDesk: {config.curr_desk},   Prev Desk: {config.prev_curr_desk}'
            print(msg)

        return fn

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        # wheel up or down
        down = event.angleDelta().y() < 0
        curr_desk = desk_manager.get_curr_desktop_number()

        if down:
            if curr_desk > 0:
                curr_desk -= 1
        else:  # wheel up
            if curr_desk < config.desk_count:
                curr_desk += 1

        desk_info.go_to_desk(curr_desk)
        super(MainWidget, self).wheelEvent(event)
