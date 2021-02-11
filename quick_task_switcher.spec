# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import get_package_paths, collect_submodules

block_cipher = None

a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[],
             datas=[
                 (r'.\assets\style.css', r'.\assets'),
                 (r'.\assets\tray_icon\*', r'.\assets\tray_icon'),
                 (r'.\utils\desk_manager\VirtualDesktopAccessor.dll', r'.\utils\desk_manager'),
                 (r'.\web\frontend\dist\*', r'.\web\frontend\dist'),
                 (get_package_paths('uvicorn')[1], 'uvicorn')
             ],
             # https://stackoverflow.com/questions/64281002/pyinstaller-compiled-uvicorn-server-does-not-start-correctly
             hiddenimports=collect_submodules('uvicorn'),
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Quick Task Switcher',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Quick Task Switcher')
