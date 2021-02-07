from PyQt5 import QtWidgets
from globals import ShortcutsDesc


class HelpWindow(QtWidgets.QMainWindow):

    def __init__(self, parent):
        super(HelpWindow, self).__init__(parent)

        # title
        self.setWindowTitle("Help")

        main_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        main_widget.setLayout(layout)

        # shortcuts
        shortcuts_txt = ''
        for key, desc in ShortcutsDesc.items():
            shortcuts_txt += f'{key}: {desc}\n'
        layout.addWidget(QtWidgets.QLabel(shortcuts_txt))

        self.setCentralWidget(main_widget)
