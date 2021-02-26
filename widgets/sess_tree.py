from typing import List

from PyQt5 import QtWidgets, QtGui, QtCore

from globals import config, paths
from utils import desk_manager
from utils.icon_extractor import get_icon


class SessTreeWidget(QtWidgets.QTreeWidget):
    WIN_HWN_ROLE = 5  # for win items
    DESK_NUM_ROLE = 5  # for desk items
    ITEM_TYPE_ROLE = 6  # for both

    DESK_ITEM = 1
    WIN_ITEM = 2

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
            item = QtWidgets.QTreeWidgetItem([desk_name])
            item.setIcon(0, QtGui.QIcon(paths.iconPaths.desk(desk_idx)))
            # TODO: make editable and rename desk if edited
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled)
            item.setData(0, self.ITEM_TYPE_ROLE, self.DESK_ITEM)
            item.setData(0, self.DESK_NUM_ROLE, desk_idx)

            desk_items.append(item)

        # add to model
        self.insertTopLevelItems(0, desk_items)

        # extra item for pinned windows
        # TODO: icon for this item
        pinned_item = QtWidgets.QTreeWidgetItem(['pinned'])
        pinned_item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.insertTopLevelItem(len(desk_items), pinned_item)

        # add windows
        windows: List[desk_manager.Window] = desk_manager.get_windows_on_all_desk()
        for window in windows:
            # create item for window
            item = QtWidgets.QTreeWidgetItem([window.title])
            item.setIcon(0, QtGui.QIcon(str(get_icon(window.exe))))
            item.setData(0, self.ITEM_TYPE_ROLE, self.WIN_ITEM)
            item.setData(0, self.WIN_HWN_ROLE, window.hwnd)

            # insert at the end
            if window.is_pinned_win or window.is_pinned_app:
                # don't allow moving pinned items
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                pinned_item.insertChild(pinned_item.childCount(), item)
            else:
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)
                desk_items[window.desk_num].insertChild(desk_items[window.desk_num].childCount(), item)

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
        dragged_win_hwnd = dragged_win_item.data(0, self.WIN_HWN_ROLE)

        # move
        desk_manager.move_window_to_desktop(dragged_win_hwnd, target_desk_idx)

        super(SessTreeWidget, self).dropEvent(event)