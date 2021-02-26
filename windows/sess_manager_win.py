from PyQt5 import QtWidgets

from utils import monitors
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
        self.tree_widget = SessTreeWidget(self)
        layout.addWidget(self.tree_widget)

        self.tree_widget.header().hide()  # hide header
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setAcceptDrops(True)
        self.tree_widget.setDropIndicatorShown(True)

        self.setCentralWidget(main_widget)

    def center(self):
        first_monitor_center = monitors.get_in_view_loc()
        x = first_monitor_center[0] - self.size().width() / 2
        y = first_monitor_center[1] - self.size().height() / 2
        self.move(x, y)

    def update_and_show(self):
        # min size
        self.setMinimumSize(500, 600)

        # update windows tree (session)
        self.tree_widget.update_model()

        self.adjustSize()
        self.center()
        self.show()
