from PyQt5 import QtWidgets, QtGui, QtCore

from globals import iconPaths, config, signals
from menus import GoToMenu, actions
from utils import desk_info
from windows import MainWindow


class TrayWidget(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent: MainWindow):
        super(TrayWidget, self).__init__(parent)

        # change icon to current desk
        desk_info.update()
        self.setIcon(QtGui.QIcon(iconPaths.desk(config.curr_desk)))
        self.setVisible(True)

        # set tooltip
        self.setToolTip("Quick Task Switcher")

        # add the menu to the tray
        self.tray_menu = QtWidgets.QMenu()
        self.setContextMenu(self.tray_menu)

        # add disabled entry to display current desktop name
        self.desk_name_action = QtWidgets.QAction()
        self.desk_name_action.setDisabled(True)
        self.tray_menu.addAction(self.desk_name_action)

        actions.add_change_desk_name_action(self.tray_menu, self.parent())
        actions.add_close_action(self.tray_menu)

        # add submenu to go specific desktop
        self.goto_submenu = GoToMenu(parent=self.tray_menu)
        self.tray_menu.addMenu(self.goto_submenu)

        self.tray_menu.addSeparator()

        # add center main window action
        self.center_main_win_action = QtWidgets.QAction("Center Window")
        self.center_main_win_action.triggered.connect(self.parent().center)
        self.tray_menu.addAction(self.center_main_win_action)

        # add quit action to system tray
        self.quit_action = QtWidgets.QAction("Quit")
        self.quit_action.triggered.connect(config.quit_func)
        self.tray_menu.addAction(self.quit_action)

        # signals
        self.activated.connect(self.onActivation)
        signals.curr_desk_changed.connect(self.updateIcon)
        signals.curr_desk_name_changed.connect(self.updateDeskName)

        # initial updates
        self.updateIcon()
        self.updateDeskName()

    @QtCore.pyqtSlot()
    def onActivation(self):
        # show main window if hidden (aka minimized)
        if not self.parent().isVisible():
            self.parent().show()

    @QtCore.pyqtSlot()
    def updateIcon(self):
        # icon to current desktop number
        self.setIcon(QtGui.QIcon(iconPaths.desk(config.curr_desk)))

        self.updateDeskName()

    @QtCore.pyqtSlot()
    def updateDeskName(self):
        # set desktop name in the first menu entry
        curr_desk_name = config.json_config.desktop_names[config.curr_desk]
        txt = f'Desktop {config.curr_desk + 1}: {curr_desk_name}'
        self.desk_name_action.setText(txt)
