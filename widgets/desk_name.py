from PyQt5 import QtWidgets, QtCore, QtGui

from globals import signals, config
from utils import dialogs


class DeskNameLabel(QtWidgets.QLabel):

    def __init__(self, parent):
        super(DeskNameLabel, self).__init__(parent)

        self.setToolTip("Click to rename")
        self.setObjectName("DeskNameLabel")

        # set initial text
        self.updateText()

        # show
        self.show()

        # connect signals
        signals.currDeskChanged.connect(self.updateText)
        signals.currDeskNameChanged.connect(self.currDeskNameChanged)
        signals.deskClosed.connect(self.deskClosed)

    @QtCore.pyqtSlot()
    def deskClosed(self):
        # shift desktop names by one
        closed_desk_id = config.curr_desk

        # if last desk is closed => do nothing
        # if closed_desk_id == config.desk_count - 1:
        #     return

        for desk_id in range(closed_desk_id, config.desk_count):
            print(f'renaming desktop with id {desk_id} '
                  f'from {config.json_config.desktop_names[desk_id]} '
                  f'to {config.json_config.desktop_names[desk_id + 1]}')
            config.json_config.desktop_names[desk_id] = config.json_config.desktop_names[desk_id + 1]

    @QtCore.pyqtSlot()
    def currDeskNameChanged(self):
        # add name to history
        new_desk_name = config.json_config.desktop_names[config.curr_desk]
        if new_desk_name not in config.json_config.desktop_names_history:
            config.json_config.desktop_names_history.append(new_desk_name)

            # remove old entries if applicable
            max_size = config.json_config.desktop_names_history_max_size
            if len(config.json_config.desktop_names_history) > max_size:
                del config.json_config.desktop_names_history[:-max_size]

        self.updateText()

    @QtCore.pyqtSlot()
    def updateText(self):
        self.setText(config.json_config.desktop_names[config.curr_desk])

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == QtCore.Qt.LeftButton:
            dialogs.change_curr_desk_name(self)
