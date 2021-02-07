from PyQt5 import QtCore


class Signals(QtCore.QObject):
    currDeskChanged = QtCore.pyqtSignal()
    deskCountChanged = QtCore.pyqtSignal()


signals = Signals()
