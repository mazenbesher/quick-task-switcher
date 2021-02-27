"""
Docs:
- https://doc.qt.io/qt-5/qtreewidget.html
- https://doc.qt.io/qt-5/qtreewidgetitem.html
"""
import datetime
from typing import List

from PyQt5 import QtWidgets, QtGui, QtCore

from globals import config, paths
from utils import desk_manager, desk_info, formatters
from utils.icon_extractor import get_icon


class SessTreeWidget(QtWidgets.QTreeWidget):
    WIN_HWND_ROLE = 5  # for win items
    DESK_NUM_ROLE = 5  # for desk items
    ITEM_TYPE_ROLE = 6  # for both

    DESK_ITEM = 1
    WIN_ITEM = 2

    def __init__(self, parent):
        super(SessTreeWidget, self).__init__(parent)

        self.setColumnCount(2)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

        # header
        # self.header().hide()
        self.headerItem().setText(0, 'Window')
        self.headerItem().setText(1, 'Duration')
        self.header().resizeSection(0, 350)

        # right click menu: https://www.qtcentre.org/threads/18929-QTreeWidgetItem-have-contextMenu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_item_context_menu)

    @QtCore.pyqtSlot(QtCore.QPoint)
    def show_item_context_menu(self, pos: QtCore.QPoint):
        item: QtWidgets.QTreeWidgetItem = self.itemAt(pos)

        # item represents a window?
        if item.data(0, self.ITEM_TYPE_ROLE) == self.WIN_ITEM:
            # create right click menu with close option
            menu = QtWidgets.QMenu(self)

            # close action
            close_action = menu.addAction('Close')
            close_action.triggered.connect(self.create_win_close_fn(item))

            menu.exec_(self.viewport().mapToGlobal(pos))

        # item represents a desk?
        if item.data(0, self.ITEM_TYPE_ROLE) == self.DESK_ITEM:
            # create right click menu
            menu = QtWidgets.QMenu(self)

            # go to desk
            desk_num = item.data(0, self.DESK_NUM_ROLE)
            go_to_action = menu.addAction('Go to')
            go_to_action.triggered.connect(desk_info.create_go_to_desk_func(desk_num))

            # TODO: rename desk

            menu.exec_(self.viewport().mapToGlobal(pos))

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        item: QtWidgets.QTreeWidgetItem = self.itemAt(event.pos())

        # item represents a desk?
        if item.data(0, self.ITEM_TYPE_ROLE) == self.DESK_ITEM:
            # double click desk item to go to that desk
            desk_num = item.data(0, self.DESK_NUM_ROLE)
            desk_info.go_to_desk(desk_num)

            # prevent default behavior (collapse in this case!)
            event.accept()

    def create_win_close_fn(self, item: QtWidgets.QTreeWidgetItem):
        assert item.data(0, self.ITEM_TYPE_ROLE) == self.WIN_ITEM

        # get hwnd
        hwnd = item.data(0, self.WIN_HWND_ROLE)

        @QtCore.pyqtSlot()
        def fn():
            # close
            if desk_manager.close_hwnd(hwnd):
                # remove child item (get parent which is the desk item and then
                # remove itself which is the child)
                item.parent().removeChild(item)

        return fn

    def update_model(self):
        # remove previous items
        self.clear()

        # disable drag to parent
        self.invisibleRootItem().setFlags(QtCore.Qt.ItemIsEnabled)

        # create item for each desktop
        desk_items = []
        for desk_idx in range(config.desk_count):
            desk_name = config.json_config.desktop_names[desk_idx]

            # create item
            item = QtWidgets.QTreeWidgetItem(self)
            item.setText(0, desk_name)
            item.setIcon(0, QtGui.QIcon(paths.iconPaths.desk(desk_idx)))
            # TODO: make editable and rename desk if edited
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled)
            item.setData(0, self.ITEM_TYPE_ROLE, self.DESK_ITEM)
            item.setData(0, self.DESK_NUM_ROLE, desk_idx)
            item.setToolTip(0, f'Double click to go to {desk_name}')

            desk_items.append(item)

        # add to model
        self.insertTopLevelItems(0, desk_items)

        # extra item for pinned windows
        # TODO: icon for this item
        pinned_item = QtWidgets.QTreeWidgetItem(['pinned'])
        pinned_item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.insertTopLevelItem(len(desk_items), pinned_item)

        # add windows
        now = datetime.datetime.now()
        windows: List[desk_manager.Window] = desk_manager.get_windows_on_all_desk()
        for window in windows:
            # determine parent
            if window.is_pinned_win or window.is_pinned_app:
                parent = pinned_item
            else:
                parent = desk_items[window.desk_num]

            # create item for window
            item = QtWidgets.QTreeWidgetItem(parent)

            # first col: window title + icon
            item.setText(0, window.title)
            item.setIcon(0, QtGui.QIcon(str(get_icon(window.exe))))
            item.setData(0, self.ITEM_TYPE_ROLE, self.WIN_ITEM)
            item.setData(0, self.WIN_HWND_ROLE, window.hwnd)

            # second col: duration
            dur_sec: float = now.timestamp() - desk_manager.get_create_time(window.pid)
            item.setText(1, formatters.duration(dur_sec))

            # set flags
            if window.is_pinned_win or window.is_pinned_app:
                # don't allow moving pinned items
                item.setFlags(QtCore.Qt.ItemIsEnabled)
            else:
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)

        # expand parents
        for item in desk_items:
            item.setExpanded(True)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        drop_target_item = self.itemAt(event.pos())

        # get parent desk item
        drop_target_desk_item = drop_target_item
        drop_target_item_type = drop_target_item.data(0, self.ITEM_TYPE_ROLE)
        if drop_target_item_type == self.WIN_ITEM:
            # dragged to a child (win item)?
            drop_target_desk_item = drop_target_item.parent()
        target_desk_idx = drop_target_desk_item.data(0, self.DESK_NUM_ROLE)

        # currently selected item == window dropped
        dragged_win_item = self.currentItem()
        dragged_win_hwnd = dragged_win_item.data(0, self.WIN_HWND_ROLE)

        # move
        desk_manager.move_window_to_desktop(dragged_win_hwnd, target_desk_idx)

        super(SessTreeWidget, self).dropEvent(event)
