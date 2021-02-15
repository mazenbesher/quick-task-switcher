from PyQt5 import QtCore


class Signals(QtCore.QObject):
    curr_desk_changed = QtCore.pyqtSignal()
    new_desk = QtCore.pyqtSignal()
    desk_closed = QtCore.pyqtSignal()
    curr_desk_name_changed = QtCore.pyqtSignal()


signals = Signals()
