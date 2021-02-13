import winreg

from .constants import RegConstants


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
