"""
Adapted from: https://stackoverflow.com/a/15898768/1617883
"""

import ctypes.wintypes

from PyQt5 import QtCore

from globals import signals
from utils import desk_manager


class QtWindowWatcher(QtCore.QRunnable):
    WINEVENT_OUTOFCONTEXT = 0x0000

    # https://docs.microsoft.com/en-us/windows/win32/winauto/event-constants
    EVENT_SYSTEM_FOREGROUND = 0x0003

    user32 = ctypes.windll.user32
    ole32 = ctypes.windll.ole32

    ole32.CoInitialize(0)

    WinEventProcType = ctypes.WINFUNCTYPE(
        None,
        ctypes.wintypes.HANDLE,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.HWND,
        ctypes.wintypes.LONG,
        ctypes.wintypes.LONG,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.DWORD
    )

    def __init__(self, *args, **kwargs):
        super(QtWindowWatcher, self).__init__(*args, **kwargs)

        def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            signals.foreground_window_changed.emit(hwnd)

        self.WinEventProc = self.WinEventProcType(callback)

        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwineventhook
        self.user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE
        self.hook = self.user32.SetWinEventHook(
            self.EVENT_SYSTEM_FOREGROUND,
            self.EVENT_SYSTEM_FOREGROUND,
            0,
            self.WinEventProc,
            0,
            0,
            self.WINEVENT_OUTOFCONTEXT
        )

        if self.hook == 0:
            raise RuntimeError('SetWinEventHook failed')

    @QtCore.pyqtSlot()
    def run(self):
        pass
        # self.msg = ctypes.wintypes.MSG()
        # while self.user32.GetMessageW(ctypes.byref(self.msg), 0, 0, 0) != 0:
        #     self.user32.TranslateMessageW(self.msg)
        #     self.user32.DispatchMessageW(self.msg)
        # self.user32.UnhookWinEvent(self.hook)
        # self.ole32.CoUninitialize()


if __name__ == '__main__':
    import sys

    from PyQt5 import QtWidgets, QtCore


    class MainWidget(QtWidgets.QWidget):
        def __init__(self, parent):
            super(MainWidget, self).__init__(parent)

            layout = QtWidgets.QVBoxLayout()

            self.label = QtWidgets.QLabel('Hello World')
            self.label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(self.label)

            self.btn = QtWidgets.QPushButton('Press me')
            self.btn.clicked.connect(self.btn_clicked)
            layout.addWidget(self.btn)

            self.setLayout(layout)

            self.threadpool = QtCore.QThreadPool()
            self.win_watcher = QtWindowWatcher()
            self.threadpool.start(self.win_watcher)

            signals.foreground_window_changed.connect(self.fg_win_changed)

        @QtCore.pyqtSlot(int)
        def fg_win_changed(self, hwnd):
            win = desk_manager.get_hwnd_window(hwnd)
            print(f'new fg window: {win.proc_name} {win.title}')

        @QtCore.pyqtSlot()
        def btn_clicked(self):
            self.label.setText('Pressed!!!')


    class MainWin(QtWidgets.QMainWindow):
        def __init__(self, parent=None):
            super(MainWin, self).__init__(parent)

            self.setCentralWidget(MainWidget(self))
            self.show()


    def main():
        app = QtWidgets.QApplication(sys.argv)

        main_window = MainWin()

        sys.exit(app.exec_())


    main()
