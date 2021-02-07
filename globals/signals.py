from PyQt5 import QtCore


class Signals(QtCore.QObject):
    currDeskChanged = QtCore.pyqtSignal()
    newDesk = QtCore.pyqtSignal()
    deskClosed = QtCore.pyqtSignal()
    currDeskNameChanged = QtCore.pyqtSignal()


signals = Signals()
