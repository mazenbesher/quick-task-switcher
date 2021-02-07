import keyboard
from PyQt5 import QtCore, QtWidgets, QtGui

from utils import desk_info, desk_manager
from globals import signals, config


class DeskNumKeysWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super(DeskNumKeysWidget, self).__init__(parent)

        # style
        self.setStyleSheet('''
            QPushButton {
                margin: 0px;
                padding: 0px;

                border-width: 1px;
                border-style: solid;
                border-color: black;
            }

            QPushButton[active=true] {
                background-color: yellow;
            }

            QPushButton:disabled  {
                border-color: gray;
            }

            QPushButton#NewDeskBtn {
                background-color: red;
            }
            ''')

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

            # margins
            desk_num_btn.setContentsMargins(0, 0, 0, 0)

            # set size
            desk_num_btn.setFixedSize(17, 25)

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
        new_desk_btn.setContentsMargins(0, 0, 0, 0)
        new_desk_btn.setFixedSize(17, 25)
        new_desk_btn.clicked.connect(lambda: keyboard.press_and_release('ctrl+win+d'))
        new_desk_btn.setObjectName('NewDeskBtn')
        layout.addWidget(new_desk_btn)

        # connect signals
        signals.currDeskChanged.connect(self.updateBtnsColor)
        signals.deskCountChanged.connect(self.updateBtnsDisabledState)

    @QtCore.pyqtSlot()
    def updateBtnsColor(self):
        for desk_num_btn in self.desk_num_btns:
            btn_desk_num = int(desk_num_btn.text())

            # active state (for styling)
            if config.currDesk == btn_desk_num:
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
            if btn_desk_num > config.deskCount:
                desk_num_btn.setDisabled(True)
            else:
                desk_num_btn.setDisabled(False)

    def newDeskCount(self, desk_count: int):
        self.updateBtnsDisabledState()

    def onDeskNumClick(self, desk_num: int):
        def onClick():
            desk_info.go_to_desk(desk_num)

        return onClick

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        # wheel up or down
        down = event.angleDelta().y() < 0
        curr_desk = desk_manager.get_curr_desktop_number()

        if down:
            if curr_desk > 0:
                curr_desk -= 1
        else:  # wheel up
            if curr_desk < config.deskCount - 1:
                curr_desk += 1

        desk_info.go_to_desk(curr_desk + 1)
        super(DeskNumKeysWidget, self).wheelEvent(event)
