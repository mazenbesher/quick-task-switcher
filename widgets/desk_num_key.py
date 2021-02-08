import keyboard
from PyQt5 import QtCore, QtWidgets, QtGui

from utils import desk_info, desk_manager
from globals import signals, config


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

            # margins
            # desk_num_btn.setContentsMargins(0, 0, 0, 0)

            # set size
            # desk_num_btn.setFixedSize(17, 25)

            # add click handler
            desk_num_btn.clicked.connect(self.onDeskNumClick(btn_desk_num))

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
                desk_num_btn.setDisabled(True)
            else:
                desk_num_btn.setDisabled(False)

    def newDeskCount(self, desk_count: int):
        self.updateBtnsDisabledState()

    def onDeskNumClick(self, desk_num: int):
        def onClick():
            desk_info.go_to_desk(desk_num)

        return onClick
