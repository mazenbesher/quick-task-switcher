from PyQt5 import QtGui

from globals import signals, config, iconPaths
from utils import desk_manager


def go_to_desk(desk_num: int):
    """
    :param desk_num: one-based index
    :return:
    """
    config.tray.setIcon(QtGui.QIcon(iconPaths.desk(desk_num)))
    desk_manager.go_to_desk_number(desk_num - 1)
    update(None, desk_num)


def update(desk_count: int = None, curr_desk: int = None):
    prev_desk_count = config.deskCount
    prev_curr_desk = config.currDesk

    # update desk count
    if desk_count is None:
        config.deskCount = desk_manager.get_desktop_count()
    else:
        config.deskCount = desk_count

    # new desk count?
    new_desk_count = False
    if prev_desk_count is not None:
        if prev_curr_desk != config.deskCount:
            new_desk_count = True
    else:
        new_desk_count = True

    # take actions!
    if new_desk_count:
        signals.deskCountChanged.emit()

    # update curr desk
    if curr_desk is None:
        config.currDesk = desk_manager.get_curr_desktop_number() + 1
    else:
        config.currDesk = curr_desk

    # new curr desk?
    new_curr_desk = False
    if prev_curr_desk is not None:
        if prev_curr_desk != config.currDesk:
            new_curr_desk = True
    else:
        new_curr_desk = True

    # take actions!
    if new_curr_desk:
        signals.currDeskChanged.emit()
