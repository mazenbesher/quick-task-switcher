from PyQt5 import QtWidgets

from globals import config, signals


def change_curr_desk_name(parent: QtWidgets.QWidget):
    # change current desktop name
    curr_desk_name = config.json_config.desktop_names[config.curr_desk]

    # create input dialog with editable combobox from previous desktops
    options = [curr_desk_name] + config.json_config.desktop_names_history
    new_desk_name_input, ok = QtWidgets.QInputDialog.getItem(parent,
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
            QtWidgets.QMessageBox.critical(parent, 'Invalid Name', 'Entered name is empty!')
            valid_name = False
        if len(new_desk_name_input) > config.json_config.desk_name_char_limit:
            QtWidgets.QMessageBox.critical(parent, 'Invalid Name',
                                           f'Name must have less than {config.json_config.desk_name_char_limit} characters')
            valid_name = False
        if new_desk_name_input == curr_desk_name:
            QtWidgets.QMessageBox.critical(parent, 'Invalid Name', 'Same old name has been entered')
            valid_name = False

        # change name!
        if valid_name:
            config.json_config.desktop_names[config.curr_desk] = new_desk_name_input

            # publish
            signals.currDeskNameChanged.emit()
