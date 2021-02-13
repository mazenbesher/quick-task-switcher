import ctypes
import ctypes.wintypes
import threading
import winreg
from typing import Callable, Optional

from .constants import RegConstants
from .exceptions import CallbackAlreadyRegistered, RegKeysNotExist
from .utils import refresh_key


class WaitRegChangeThread(threading.Thread):
    def __init__(self, reg_key_path: bytes, callback: Callable, *args, **kwargs):
        super(WaitRegChangeThread, self).__init__(*args, **kwargs)
        self.callback = callback
        self.reg_key_path = reg_key_path
        self._stop_ev = threading.Event()

    def stop(self) -> None:
        self._stop_ev.set()

    def run(self) -> None:
        while not self._stop_ev.is_set():
            hdl = ctypes.wintypes.HKEY()
            res = RegConstants.RegOpenKeyExA(RegConstants.HKEY_CURRENT_USER, self.reg_key_path, 0,
                                             RegConstants.KEY_NOTIFY, hdl)
            if res != 0: raise RuntimeError(f'RegOpenKeyExA failed, error {res}')
            res = RegConstants.RegNotifyChangeKeyValue(hdl, False, RegConstants.REG_NOTIFY_CHANGE_LAST_SET, None, False)
            if res != 0: raise RuntimeError(f'RegNotifyChangeKeyValue failed, error {res}')
            self.callback()
            RegConstants.RegCloseKey(hdl)


class DesktopWatcher:
    def __init__(self):
        # make sure the keys exist
        try:
            for key_path in [RegConstants.all_vdesk_ids_key_path, RegConstants.curr_vdesk_id_key_path]:
                key_handler = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
                winreg.CloseKey(key_handler)
        except FileNotFoundError:
            raise RegKeysNotExist

        # threads
        self.desk_change_thread: Optional[WaitRegChangeThread] = None
        self.desk_count_change_thread: Optional[WaitRegChangeThread] = None

    def register_desk_change_callback(self, callback: Callable):
        """
        Note: the callback is called one extra time when the watcher is stopped
        Note: the callback function must be thread-safe (see utils.desk_info.update)
        """
        if self.desk_change_thread is not None:
            raise CallbackAlreadyRegistered

        self.desk_change_thread = WaitRegChangeThread(
            RegConstants.curr_vdesk_id_key_path.encode(),
            callback,
        )
        self.desk_change_thread.start()

    def register_desk_count_change_callback(self, callback: Callable):
        """
        Note: the callback is called one extra time when the watcher is stopped
        Note: the callback function must be thread-safe (see utils.desk_info.update)
        """

        if self.desk_count_change_thread is not None:
            raise CallbackAlreadyRegistered

        self.desk_count_change_thread = WaitRegChangeThread(
            RegConstants.all_vdesk_ids_key_path.encode(),
            callback,
        )
        self.desk_count_change_thread.start()

    def stop(self):
        """
        Note: the callbacks are called one extra time when the watcher is stopped

        TODO: this method uses a workaround to force the threads to stop (by forcing a notification on the regkey value
        to force each thread to go over the RegConstants.RegNotifyChangeKeyValue line)
        """
        if self.desk_change_thread is not None and self.desk_change_thread.is_alive():
            self.desk_change_thread.stop()
            refresh_key(RegConstants.curr_vdesk_id_key_path)

        if self.desk_count_change_thread is not None and self.desk_count_change_thread.is_alive():
            self.desk_count_change_thread.stop()
            refresh_key(RegConstants.all_vdesk_ids_key_path)


if __name__ == "__main__":
    import time

    watcher = DesktopWatcher()

    print('start')
    watcher.register_desk_change_callback(lambda: print('Desktop changed'))
    watcher.register_desk_count_change_callback(lambda: print('Desktop count changed'))

    print('wait')
    time.sleep(4)

    print('terminating')
    watcher.stop()

    print('end')
