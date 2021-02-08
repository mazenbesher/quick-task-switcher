from PyQt5 import QtWidgets, QtCore, QtGui

from globals import config


class GrabWidget(QtWidgets.QWidget):
    def __init__(self, parent, grab_button: QtCore.Qt.MouseButton = QtCore.Qt.LeftButton,
                 move_target: QtWidgets.QWidget = None):
        super().__init__(parent)

        self.move_target = move_target or self.window()
        self.grab_button = grab_button

        self.setToolTip("Drag to move window")
        self.setObjectName("GrabWidget")

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )

    def sizeHint(self):
        return QtCore.QSize(*config.json_config.grab_area_min_size)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)

        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor("gray"))
        brush.setStyle(QtCore.Qt.Dense7Pattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == self.grab_button:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(GrabWidget, self).mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == self.grab_button:
            # adjust offset from clicked point to origin of widget
            curr_pos = self.mapToGlobal(self.move_target.pos())
            global_pos = event.globalPos()
            diff = global_pos - self.__mouseMovePos
            new_pos = self.mapFromGlobal(curr_pos + diff)
            self.move_target.move(new_pos)

            self.__mouseMovePos = global_pos

        super(GrabWidget, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(GrabWidget, self).mouseMoveEvent(event)
