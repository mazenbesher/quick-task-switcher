from PyQt5 import QtWidgets

from utils import monitors


class Base(QtWidgets.QWidget):
    def center_and_move(self):
        first_monitor_center = monitors.get_in_view_loc()
        x = first_monitor_center[0] - self.size().width() / 2
        y = first_monitor_center[1] - self.size().height() / 2
        self.move(x, y)
