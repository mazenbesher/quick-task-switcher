import ctypes
import ctypes.wintypes
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Literal


# from dataclasses_json import dataclass_json


# @dataclass_json
@dataclass
class Window:
    title: str
    hwnd: int
    is_pinned_win: bool
    is_pinned_app: bool
    desk_num: int
    pid: int
    proc_name: str


enumWindows = ctypes.windll.user32.EnumWindows
enumDesktopWindows = ctypes.windll.user32.EnumDesktopWindows
enumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
getWindowText = ctypes.windll.user32.GetWindowTextW
getWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
isWindowVisible = ctypes.windll.user32.IsWindowVisible
psapi = ctypes.WinDLL('Psapi.dll')

"""https://github.com/Ciantic/VirtualDesktopAccessor"""
curr_path = Path(__file__).parent.absolute()
vda_dll_name = 'VirtualDesktopAccessor.dll'
vda_dll_path = curr_path / vda_dll_name
vda = ctypes.cdll.LoadLibrary(str(vda_dll_path))

default_excluded_apps_titles = [
    'Task View Controller',
    'XYplorer',
    'Alarms & Clock',
    'Calculator',
    'Dynamic Theme',
    'Settings',
    'Microsoft Store',
    'Microsoft Text Input Application',
    'NVIDIA GeForce Overlay',
    'Switch USB',
    'Program Manager',
]


def get_hwnd_title(hwnd: int) -> str:
    length = getWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    getWindowText(hwnd, buff, length + 1)
    return buff.value


def get_windows_on_all_desk() -> List[Window]:
    windows = []

    def foreach_window(hwnd, lParam):
        if isWindowVisible(hwnd):
            title = get_hwnd_title(hwnd)
            if len(title) != 0 and title not in default_excluded_apps_titles:
                windows.append(get_hwnd_window(hwnd))
        return True

    enumWindows(enumWindowsProc(foreach_window), 0)
    return windows


def get_windows_on_curr_desk() -> List[Window]:
    return list(
        filter(
            lambda w: vda.IsWindowOnCurrentVirtualDesktop(w.hwnd) == 1,
            get_windows_on_all_desk()
        )
    )


def get_windows_on_desk(desk: int) -> List[Window]:
    return list(
        filter(
            lambda w: vda.IsWindowOnDesktopNumber(w.hwnd, desk - 1) == 1,
            get_windows_on_all_desk()
        )
    )


def move_window_to_desktop(win_to_move_hwnd: int, desk: int):
    def foreach_window(hwnd, lParam):
        if isWindowVisible(hwnd):
            if hwnd == win_to_move_hwnd:
                vda.MoveWindowToDesktopNumber(hwnd, desk - 1)
                return False  # stop iteration
        return True

    enumWindows(enumWindowsProc(foreach_window), 0)


def pin_win(hwnd: int):
    vda.PinWindow(hwnd)


def pin_app(hwnd: int):
    vda.PinApp(hwnd)


def get_foreground_window() -> Window:
    return get_hwnd_window(ctypes.windll.user32.GetForegroundWindow())


def get_hwnd_window(hwnd: int) -> Window:
    pid = get_pid(hwnd)
    return Window(
        hwnd=hwnd,
        desk_num=vda.GetWindowDesktopNumber(hwnd) + 1,
        title=get_hwnd_title(hwnd),
        is_pinned_win=bool(vda.IsPinnedWindow(hwnd)),
        is_pinned_app=bool(vda.IsPinnedApp(hwnd)),
        pid=pid,
        proc_name=get_proc_name(pid),
    )


def switch_to(hwnd: int):
    """Switch to window like Alt+Tab switcher"""
    print(vda.ViewSwitchTo(hwnd))


def get_pid(hwnd: int) -> int:
    lpdw_process_id = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(lpdw_process_id))
    return lpdw_process_id.value


def get_proc_name(pid: int, strip_exe: bool = True) -> str:
    """https://stackoverflow.com/a/6981360/1617883"""
    MAX_PATH = 260
    PROCESS_QUERY_INFORMATION = 0x0400

    filename = b''
    hProcess = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
    if hProcess:
        ImageFileName = (ctypes.c_char * MAX_PATH)()
        if psapi.GetProcessImageFileNameA(hProcess, ImageFileName, MAX_PATH) > 0:
            filename: bytes = os.path.basename(ImageFileName.value)
            if strip_exe and filename.endswith(b'.exe'):
                filename = filename[:-4]
        ctypes.windll.kernel32.CloseHandle(hProcess)
    return filename.decode()


# def print_windows(windows: List[Window]):
#     from tabulate import tabulate
#
#     all_fields = list(Window.schema().fields.keys())
#     to_print = []
#     for i, w in enumerate(windows):
#         to_print.append([i] + [getattr(w, attr) for attr in all_fields])
#     print(tabulate(to_print, headers=['#'] + all_fields))


def get_win_rect(hwnd: int) -> ctypes.wintypes.RECT:
    """
    https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowrect

    left;        // x position of upper-left corner
    top;         // y position of upper-left corner
    right;       // x position of lower-right corner
    bottom;      // y position of lower-right corner
    """
    win_rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(win_rect))
    return win_rect


def get_desktop_count() -> int:
    return vda.GetDesktopCount()


def get_curr_desktop_number() -> int:
    """
    Note: zero based desktop number
    """
    return vda.GetCurrentDesktopNumber()


def go_to_desk_number(desk_num: int):
    """
    Note: zero based desktop number
    """
    vda.GoToDesktopNumber(desk_num)


if __name__ == '__main__':
    if False:
        go_to_desk_number(1)
        print(get_curr_desktop_number())
        print(get_desktop_count())

    if False:
        windows = get_windows_on_all_desk()
        print('Windows on all desktops:')
        print_windows(windows)

    if False:
        fwin = get_foreground_window()
        rect = get_win_rect(fwin.hwnd)
        print(rect.left, rect.top, rect.right, rect.bottom)

    if False:
        # list windows
        windows = get_windows_on_curr_desk()
        print('Windows on current desktop:')
        print_windows(windows)

    if False:
        # test moving  notepad
        windows = get_windows_on_all_desk()
        for w in windows:
            if 'notepad' in w.title.lower():
                move_window_to_desktop(w.hwnd, 1)

    if False:
        # test get foreground window
        fwin = get_foreground_window()
        print(fwin)

    if False:
        # test switch to
        windows = get_windows_on_all_desk()
        for w in windows:
            if 'potplayer' in w.title.lower():
                switch_to(w.hwnd)
