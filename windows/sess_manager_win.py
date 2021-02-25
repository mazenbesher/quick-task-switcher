from PyQt5 import QtWidgets

from widgets.sess_tree import SessTreeWidget


class SessManagerWindow(QtWidgets.QMainWindow):
    def __init__(self, parent):
        super(SessManagerWindow, self).__init__(parent)

        # title
        self.setWindowTitle("Session Manager")

        main_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        main_widget.setLayout(layout)

        # create tree view
        self.tree_widget = SessTreeWidget()
        layout.addWidget(self.tree_widget)

        self.tree_widget.header().hide()  # hide header
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setAcceptDrops(True)
        self.tree_widget.setDropIndicatorShown(True)

        self.setCentralWidget(main_widget)
