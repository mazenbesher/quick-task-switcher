import ctypes
import ctypes.wintypes
import threading
import winreg

from PyQt5 import QtCore

from .constants import RegConstants
from .exceptions import RegKeysNotExist
from .utils import refresh_key


class WaitRegChangeSignals(QtCore.QObject):
    value_changed = QtCore.pyqtSignal()


class WaitRegChangeQtThread(QtCore.QRunnable):
    def __init__(self, reg_key_path: bytes, *args, **kwargs):
        super(WaitRegChangeQtThread, self).__init__(*args, **kwargs)
        self.reg_key_path = reg_key_path
        self._stop_ev = threading.Event()
        self.signals = WaitRegChangeSignals()

    def stop(self) -> None:
        self._stop_ev.set()

    @QtCore.pyqtSlot()
    def run(self) -> None:
        while not self._stop_ev.is_set():
            hdl = ctypes.wintypes.HKEY()
            res = RegConstants.RegOpenKeyExA(RegConstants.HKEY_CURRENT_USER, self.reg_key_path, 0,
                                             RegConstants.KEY_NOTIFY, hdl)
            if res != 0: raise RuntimeError(f'RegOpenKeyExA failed, error {res}')
            res = RegConstants.RegNotifyChangeKeyValue(hdl, False, RegConstants.REG_NOTIFY_CHANGE_LAST_SET, None, False)
            if res != 0: raise RuntimeError(f'RegNotifyChangeKeyValue failed, error {res}')
            self.signals.value_changed.emit()
            RegConstants.RegCloseKey(hdl)


class DesktopWatcherQtSignals(QtCore.QObject):
    desk_changed = QtCore.pyqtSignal()
    desk_count_changed = QtCore.pyqtSignal()


class DesktopWatcherQt(QtCore.QObject):
    def __init__(self):
        super(DesktopWatcherQt, self).__init__()

        # make sure the keys exist
        try:
            for key_path in [RegConstants.all_vdesk_ids_key_path, RegConstants.curr_vdesk_id_key_path]:
                key_handler = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
                winreg.CloseKey(key_handler)
        except FileNotFoundError:
            raise RegKeysNotExist

        # signals
        self.signals = DesktopWatcherQtSignals()

        # threads
        self.threadpool = QtCore.QThreadPool()

        self.desk_change_thread = WaitRegChangeQtThread(RegConstants.curr_vdesk_id_key_path.encode())
        self.desk_change_thread.signals.value_changed.connect(self.signals.desk_changed.emit)
        self.threadpool.start(self.desk_change_thread)

        self.desk_count_change_thread = WaitRegChangeQtThread(RegConstants.all_vdesk_ids_key_path.encode())
        self.desk_count_change_thread.signals.value_changed.connect(self.signals.desk_count_changed.emit)
        self.threadpool.start(self.desk_count_change_thread)

    def stop(self):
        """
        Note: the callbacks are called one extra time when the watcher is stopped

        TODO: this method uses a workaround to force the threads to stop (by forcing a notification on the regkey value
        to force each thread to go over the RegConstants.RegNotifyChangeKeyValue line)
        """
        self.desk_change_thread.stop()
        refresh_key(RegConstants.curr_vdesk_id_key_path)

        self.desk_count_change_thread.stop()
        refresh_key(RegConstants.all_vdesk_ids_key_path)
