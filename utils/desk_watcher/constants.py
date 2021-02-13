import ctypes.wintypes
from dataclasses import dataclass


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
