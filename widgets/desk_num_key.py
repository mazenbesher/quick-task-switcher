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
        for btn_desk_num in range(1, 10):
            desk_num_btn = QtWidgets.QPushButton(str(btn_desk_num))

            # set object name
            desk_num_btn.setObjectName("DeskNumBtn")

            # set tooltip to desktop name
            desk_num_btn.setToolTip(config.json_config.desktop_names[btn_desk_num - 1])

            # add click handler
            desk_num_btn.clicked.connect(desk_info.create_go_to_desk_func(btn_desk_num))

            # add to layout
            layout.addWidget(desk_num_btn)
            self.desk_num_btns.append(desk_num_btn)

        # update buttons states
        desk_info.update()
        self.updateBtnsColor()
        self.updateBtnsDisabledState()

        # new desk button
        new_desk_btn = QtWidgets.QPushButton('+')
        # new_desk_btn.setContentsMargins(0, 0, 0, 0)
        # new_desk_btn.setFixedSize(17, 25)
        new_desk_btn.clicked.connect(self.newDesk)
        new_desk_btn.setObjectName('NewDeskBtn')
        layout.addWidget(new_desk_btn)

        # connect signals
        signals.currDeskChanged.connect(self.updateBtnsColor)
        signals.newDesk.connect(self.updateBtnsDisabledState)
        signals.deskClosed.connect(self.updateBtnsDisabledState)
        signals.currDeskNameChanged.connect(self.updateCurrDeskBtnTooltip)

    @QtCore.pyqtSlot()
    def updateCurrDeskBtnTooltip(self):
        curr_desk_id = config.curr_desk - 1
        self.desk_num_btns[curr_desk_id].setToolTip(config.json_config.desktop_names[curr_desk_id])

    def newDesk(self):
        keyboard.press_and_release('ctrl+win+d')
        desk_info.update()

    @QtCore.pyqtSlot()
    def updateBtnsColor(self):
        for desk_num_btn in self.desk_num_btns:
            btn_desk_num = int(desk_num_btn.text())

            # active state (for styling)
            if config.curr_desk == btn_desk_num:
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
