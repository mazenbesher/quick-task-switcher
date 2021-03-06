import threading
from typing import Tuple

from globals import signals, config
from utils import desk_manager

update_desk_info_lock = threading.Lock()
first_call = True


def go_to_desk(desk_num: int):
    assert 0 <= desk_num < config.desk_count
    desk_manager.go_to_desk_number(desk_num)
    update(None, desk_num)


def update_desk_count(desk_count: int = None) -> Tuple[bool, bool]:
    """
    :param desk_count:
    :return: True if desktop count changed
    """
    prev_desk_count = config.desk_count

    # update desk count
    new_desk_count = desk_count
    if desk_count is None:
        new_desk_count = desk_manager.get_desktop_count()
    config.desk_count = new_desk_count

    # events
    new_desk = False
    desk_closed = False
    if prev_desk_count is not None and prev_desk_count != config.desk_count:
        config.prev_desk_count = prev_desk_count
        if prev_desk_count > new_desk_count:
            desk_closed = True
        elif prev_desk_count < new_desk_count:
            new_desk = True

    return new_desk, desk_closed


def update_curr_desk(curr_desk: int = None):
    """
    :param curr_desk:
    :return: True if current desktop changed
    """
    prev_curr_desk = config.curr_desk

    # update curr desk
    if curr_desk is None:
        config.curr_desk = desk_manager.get_curr_desktop_number()
    else:
        config.curr_desk = curr_desk

    # new curr desk?
    new_curr_desk = False
    if prev_curr_desk is not None:
        if prev_curr_desk != config.curr_desk:
            config.prev_curr_desk = prev_curr_desk
            new_curr_desk = True
    else:
        new_curr_desk = True

    return new_curr_desk


def update(desk_count: int = None, curr_desk: int = None):
    global first_call

    # prevent race-condition to update desktop info multiple times from multiple threads
    # this can happened because of the DeskWatcher class which uses two threads to monitor current and total number
    # of virtual desktops
    # both of these threads are connected to this function as callback
    with update_desk_info_lock:
        new_desk, desk_closed = update_desk_count(desk_count)

        if config.desk_count > config.json_config.desktops_number:
            # TODO: this message is blocked and cannot be confirmed
            # QtWidgets.QMessageBox.critical(None, *messages.unsupported_desktops())
            config.quit_func()
            return

        if new_desk and not first_call:
            # new desk actions
            signals.new_desk.emit()
        if desk_closed and not first_call:
            # desk closed actions
            signals.desk_closed.emit()

        if update_curr_desk(curr_desk) and not first_call:
            # new desk actions
            signals.curr_desk_changed.emit()

        first_call = False


def create_go_to_desk_func(desk_num: int):
    def fn():
        if desk_num < config.desk_count and desk_num != config.curr_desk:
            go_to_desk(desk_num)

    return fn
