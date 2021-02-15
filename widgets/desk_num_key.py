import keyboard
from PyQt5 import QtCore, QtWidgets

from globals import signals, config
from utils import desk_info


class DeskNumKeysWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super(DeskNumKeysWidget, self).__init__(parent)

        # set name (for css ref for instance)
        self.setObjectName("DeskNumKeysWidget")

        # layout
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(layout)

        # desk num buttons
        self.desk_num_btns = []
        for desk_idx in range(config.json_config.desktops_number):
            desk_num_btn = QtWidgets.QPushButton(str(desk_idx + 1))

            # set object name
            desk_num_btn.setObjectName("DeskNumBtn")

            # set tooltip to desktop name
            desk_num_btn.setToolTip(config.json_config.desktop_names[desk_idx])

            # add click handler
            desk_num_btn.clicked.connect(desk_info.create_go_to_desk_func(desk_idx))

            # add to layout
            layout.addWidget(desk_num_btn)
            self.desk_num_btns.append(desk_num_btn)

        # new desk button
        self.new_desk_btn = QtWidgets.QPushButton('+')
        self.new_desk_btn.clicked.connect(lambda: keyboard.press_and_release('ctrl+win+d'))
        self.new_desk_btn.setObjectName('NewDeskBtn')
        layout.addWidget(self.new_desk_btn)

        # update buttons states
        desk_info.update()
        self.updateBtnsColor()
        self.updateBtnsDisabledState()

        # connect signals
        signals.curr_desk_changed.connect(self.updateBtnsColor)
        signals.new_desk.connect(self.updateBtnsDisabledState)
        signals.desk_closed.connect(self.updateBtnsDisabledState)
        signals.curr_desk_name_changed.connect(self.updateCurrDeskBtnTooltip)

    @QtCore.pyqtSlot()
    def updateCurrDeskBtnTooltip(self):
        self.desk_num_btns[config.curr_desk].setToolTip(config.json_config.desktop_names[config.curr_desk])

    @QtCore.pyqtSlot()
    def updateBtnsColor(self):
        for desk_num_btn in self.desk_num_btns:
            desk_idx = int(desk_num_btn.text()) - 1

            # active state (for styling)
            if config.curr_desk == desk_idx:
                desk_num_btn.setProperty('active', True)
            else:
                desk_num_btn.setProperty('active', False)

            # Updating On Property Changes
            # see: http://dgovil.com/blog/2017/02/24/qt_stylesheets/
            desk_num_btn.setStyle(desk_num_btn.style())

    @QtCore.pyqtSlot()
    def updateBtnsDisabledState(self):
        for desk_num_btn in self.desk_num_btns:
            btn_desk_num = int(desk_num_btn.text())

            # disable state
            if btn_desk_num > config.desk_count:
                # setDisabled is not used to allow context menu (right click) pass through
                desk_num_btn.setProperty("inactive", True)
            else:
                desk_num_btn.setProperty("inactive", False)

        # if last desktop, disable add new desktop
        if config.desk_count == config.json_config.desktops_number:
            self.new_desk_btn.setDisabled(True)
        else:
            self.new_desk_btn.setDisabled(False)
