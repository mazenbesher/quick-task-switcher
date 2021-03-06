from PyQt5 import QtWidgets, QtCore

from globals import config, signals
from utils import desk_info


class GoToMenu(QtWidgets.QMenu):
    def __init__(self, label: str = 'Go To ...', parent=None):
        super(GoToMenu, self).__init__(label, parent)

        # add actions to go specific desktop
        self.actions = []
        for desk_idx in range(config.json_config.desktops_number):
            desk_name = config.json_config.desktop_names[desk_idx]
            goto_action = QtWidgets.QAction(f"Desktop {desk_idx + 1}: {desk_name}")
            if desk_idx >= config.desk_count:
                goto_action.setDisabled(True)
            goto_action.triggered.connect(desk_info.create_go_to_desk_func(desk_idx))
            self.addAction(goto_action)
            self.actions.append(goto_action)

        # signals
        signals.curr_desk_changed.connect(self.updateCurrDeskLabel)
        signals.curr_desk_name_changed.connect(self.updateCurrDeskLabel)
        signals.desk_closed.connect(self.updateDisabledStates)
        signals.new_desk.connect(self.updateDisabledStates)

        # initial updates
        self.updateCurrDeskLabel()

    @QtCore.pyqtSlot()
    def updateCurrDeskLabel(self):
        # update goto submenu text
        curr_desk_name = config.json_config.desktop_names[config.curr_desk]
        txt = f'Desktop {config.curr_desk + 1}: {curr_desk_name}'
        self.actions[config.curr_desk].setText(txt)

    @QtCore.pyqtSlot()
    def updateDisabledStates(self):
        for desk_idx in range(config.json_config.desktops_number):
            disabled = desk_idx >= config.desk_count
            self.actions[desk_idx].setDisabled(disabled)
