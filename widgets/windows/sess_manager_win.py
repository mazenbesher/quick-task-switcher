from PyQt5 import QtWidgets

from widgets.base import Base
from widgets.sess_tree import SessTreeWidget


class SessManagerWindow(QtWidgets.QMainWindow, Base):
    def __init__(self, parent):
        super(SessManagerWindow, self).__init__(parent)

        # title
        self.setWindowTitle("Session Manager")

        main_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        main_widget.setLayout(layout)

        # create tree view
        self.tree_widget = SessTreeWidget(self)
        layout.addWidget(self.tree_widget)

        self.setCentralWidget(main_widget)

    def update_and_show(self):
        # min size
        self.setMinimumSize(500, 600)

        # update windows tree (session)
        self.tree_widget.update_model()

        self.adjustSize()
        self.center_and_move()
        self.show()
