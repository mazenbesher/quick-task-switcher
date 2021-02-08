from PyQt5 import QtWidgets, QtCore, QtGui

from globals import signals, config


class DeskNameLabel(QtWidgets.QLabel):

    def __init__(self, parent):
        super(DeskNameLabel, self).__init__(parent)

        # set name (for css ref for instance)
        self.setObjectName("DeskNameLabel")

        # set initial text
        self.updateText()

        # show
        self.show()

        # connect signals
        signals.currDeskChanged.connect(self.updateText)
        signals.currDeskNameChanged.connect(self.currDeskNameChanged)
        signals.deskClosed.connect(self.deskClosed)

    @QtCore.pyqtSlot()
    def deskClosed(self):
        # shift desktop names by one
        closed_desk_id = config.curr_desk - 1

        for desk_id in range(closed_desk_id, config.desk_count - 1):
            print(
                f'renaming desktop {desk_id} from {config.json_config.desktop_names[desk_id]} to {config.json_config.desktop_names[desk_id + 1]}')
            config.json_config.desktop_names[desk_id] = config.json_config.desktop_names[desk_id + 1]

    @QtCore.pyqtSlot()
    def currDeskNameChanged(self):
        # add name to history
        new_desk_name = config.json_config.desktop_names[config.curr_desk - 1]
        config.json_config.desktop_names_history.append(new_desk_name)

        # remove old entries if applicable
        max_size = config.json_config.desktop_names_history_max_size
        if len(config.json_config.desktop_names_history) > max_size:
            del config.json_config.desktop_names_history[:-max_size]

        self.updateText()

    @QtCore.pyqtSlot()
    def updateText(self):
        self.setText(config.json_config.desktop_names[config.curr_desk - 1])

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == QtCore.Qt.LeftButton:
            # change current desktop name
            curr_desk_name = config.json_config.desktop_names[config.curr_desk - 1]

            # create input dialog with editable combobox from previous desktops
            options = [curr_desk_name] + config.json_config.desktop_names_history
            new_desk_name_input, ok = QtWidgets.QInputDialog.getItem(self,
                                                                     "New Desktop Name",
                                                                     "Desktop name:",
                                                                     options,
                                                                     0,
                                                                     True)

            # process results
            if ok:
                # validate input
                valid_name = True
                if len(new_desk_name_input) == 0:
                    QtWidgets.QMessageBox.critical(self, 'Invalid Name', 'Entered name is empty!')
                    valid_name = False
                if len(new_desk_name_input) > config.json_config.desk_name_char_limit:
                    QtWidgets.QMessageBox.critical(self, 'Invalid Name',
                                                   f'Name must have less than {config.json_config.desk_name_char_limit} characters')
                    valid_name = False
                if new_desk_name_input == curr_desk_name:
                    QtWidgets.QMessageBox.critical(self, 'Invalid Name', 'Same old name has been entered')
                    valid_name = False

                # change name!
                if valid_name:
                    config.json_config.desktop_names[config.curr_desk - 1] = new_desk_name_input

                    # publish
                    signals.currDeskNameChanged.emit()
