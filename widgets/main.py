from PyQt5 import QtCore, QtWidgets

from utils import desk_info
from .desk_num_key import DeskNumKeysWidget


class MainWidget(QtWidgets.QWidget):

    def __init__(self, parent, grabButton: QtCore.Qt.MouseButton = QtCore.Qt.LeftButton):
        super(MainWidget, self).__init__(parent)
        self.grabButton = grabButton

        # layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(DeskNumKeysWidget(self))
        self.setLayout(layout)

        # refresh desk info each second
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(desk_info.update)
        self.timer.start()

    # Grabbable (can be moved using the grabButton) main widget

    # def mousePressEvent(self, event):
    #     self.__mousePressPos = None
    #     self.__mouseMovePos = None
    #     if event.button() == self.grabButton:
    #         self.__mousePressPos = event.globalPos()
    #         self.__mouseMovePos = event.globalPos()
    #
    #     super(MainWidget, self).mouseMoveEvent(event)
    #
    # def mouseMoveEvent(self, event):
    #     if event.buttons() == self.grabButton:
    #         # adjust offset from clicked point to origin of widget
    #         currPos = self.mapToGlobal(self.parent().pos())
    #         globalPos = event.globalPos()
    #         diff = globalPos - self.__mouseMovePos
    #         newPos = self.mapFromGlobal(currPos + diff)
    #         self.parent().move(newPos)
    #
    #         self.__mouseMovePos = globalPos
    #
    #     super(MainWidget, self).mouseMoveEvent(event)
    #
    # def mouseReleaseEvent(self, event):
    #     if self.__mousePressPos is not None:
    #         moved = event.globalPos() - self.__mousePressPos
    #         if moved.manhattanLength() > 3:
    #             event.ignore()
    #             return
    #
    #     super(MainWidget, self).mouseMoveEvent(event)
