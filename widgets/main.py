from PyQt5 import QtCore, QtWidgets, QtGui

from globals import config, signals
from utils import desk_info, desk_manager
from .desk_name import DeskNameLabel
from .desk_num_key import DeskNumKeysWidget
from .desk_timer import DeskTimerLabel
from .grab_area_widget import GrabAreaWidget


class MainWidget(QtWidgets.QWidget):

    def __init__(self, parent, enable_logging: bool = False):
        super(MainWidget, self).__init__(parent)
        # self.grabButton = grabButton

        # set name (for css ref for instance)
        self.setObjectName("MainWidget")

        # debug all signals
        # TODO: enable only via a flag
        # TODO: automate this in a loop
        if enable_logging:
            signals.desk_closed.connect(self.signalsDebugFn('desk_closed'))
            signals.new_desk.connect(self.signalsDebugFn('new_desk'))
            signals.curr_desk_changed.connect(self.signalsDebugFn('curr_desk_changed'))
            signals.curr_desk_name_changed.connect(self.signalsDebugFn('curr_desk_name_changed'))
            signals.foreground_window_changed.connect(self.singals_debug_fg_win_changed)

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

    def signalsDebugFn(self, event_name: str):
        @QtCore.pyqtSlot()
        def fn():
            msg = event_name
            msg += f'\n\tCount: {config.desk_count}, Prev Count: {config.prev_desk_count}'
            msg += f'\n\tDesk: {config.curr_desk},   Prev Desk: {config.prev_curr_desk}'
            print(msg)

        return fn

    @QtCore.pyqtSlot(int)
    def singals_debug_fg_win_changed(self, hwnd: int):
        window = desk_manager.get_hwnd_window(hwnd)

        msg = f'Foreground window changed'
        msg += f'\n\tHWND: {hwnd}'
        msg += f'\n\tProcess: {window.proc_name}'
        msg += f'\n\tTitle: {window.title}'
        print(msg)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        # wheel up or down
        down = event.angleDelta().y() < 0

        if down:
            if config.curr_desk > 0:
                desk_info.go_to_desk(config.curr_desk - 1)
        else:  # wheel up
            if config.curr_desk < config.desk_count - 1:
                desk_info.go_to_desk(config.curr_desk + 1)

        super(MainWidget, self).wheelEvent(event)
