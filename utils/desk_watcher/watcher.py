"""
Adapted from https://gist.github.com/mooware/3466bdb9e677c871f08165484a52f523
"""

import ctypes
import ctypes.wintypes
import threading
import winreg
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class RegConstants:
    advapi32 = ctypes.windll.advapi32

    HKEY_CURRENT_USER = ctypes.wintypes.HKEY(0x80000001)
    KEY_NOTIFY = 0x0010
    REG_NOTIFY_CHANGE_LAST_SET = 0x00000004
    REG_DWORD = 4

    # LSTATUS RegOpenKeyExA(HKEY hKey, LPCSTR lpSubKey, DWORD ulOptions, REGSAM samDesired, PHKEY phkResult)
    RegOpenKeyExA = advapi32.RegOpenKeyExA
    RegOpenKeyExA.argtypes = (
        ctypes.wintypes.HKEY,
        ctypes.wintypes.LPCSTR,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.PHKEY
    )

    # https://docs.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regnotifychangekeyvalue
    # LSTATUS RegNotifyChangeKeyValue(HKEY hKey, BOOL bWatchSubtree, DWORD dwNotifyFilter, HANDLE hEvent, BOOL fAsynchronous)
    RegNotifyChangeKeyValue = advapi32.RegNotifyChangeKeyValue
    RegNotifyChangeKeyValue.argtypes = (
        ctypes.wintypes.HKEY,
        ctypes.wintypes.BOOL,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.HANDLE,
        ctypes.wintypes.BOOL
    )

    # LSTATUS RegCloseKey(HKEY hKey)
    RegCloseKey = advapi32.RegCloseKey
    RegCloseKey.argtypes = (ctypes.wintypes.HKEY,)

    # paths to virtual desktop related key in registry
    all_vdesk_ids_key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VirtualDesktops'
    curr_vdesk_id_key_path = r'Software\Microsoft\Windows\CurrentVersion\Explorer\SessionInfo\1\VirtualDesktops'


class RegKeysNotExist(Exception):
    pass


class CallbackAlreadyRegistered(Exception):
    pass


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


def refresh_key(key_path: str):
    """
    1. Open the key
    2. Get default value (marked as "(Default)" in regedit) if exists
    3. Set the key to random value => refresh any waiting notifier (via RegNotifyChangeKeyValue)
    4. Set the key to default value from step 2
    """
    assert key_path in [
        RegConstants.curr_vdesk_id_key_path,
        RegConstants.all_vdesk_ids_key_path,
    ]

    key_handler = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        key_path,
        0,
        winreg.KEY_ALL_ACCESS
    )
    try:
        def_val = winreg.QueryValueEx(key_handler, '')[0]
    except FileNotFoundError:
        def_val = ''
    winreg.SetValueEx(key_handler, '', 0, winreg.REG_SZ, '\x12')
    winreg.SetValueEx(key_handler, '', 0, winreg.REG_SZ, def_val)
    winreg.CloseKey(key_handler)


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


    def desk_change_callback():
        print('Desktop changed')


    def desk_count_change_callback():
        print('Desktop count changed')


    print('start')
    watcher.register_desk_change_callback(desk_change_callback)
    watcher.register_desk_count_change_callback(desk_count_change_callback)

    print('wait')
    time.sleep(10)

    print('terminating')
    watcher.stop()

    print('end')
