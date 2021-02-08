# Links

- VirtualDesktopAccessor: https://github.com/Ciantic/VirtualDesktopAccessor

## Docs

- System Tray: https://www.learnpyqt.com/tutorials/system-tray-mac-menu-bar-applications-pyqt/
- QInputDialog: https://doc.qt.io/qt-5/qinputdialog.html
- Packaging: https://www.learnpyqt.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/

# TODOS

- [x] system tray icon
- [ ] implement extension system with sample extensions:
    - [ ] music control
- [ ] improve packaging with a custom name and parameters
- [ ] support more than 9 desktops
- [ ] minimize

# Packaging

In the project directory execute:

```powershell
poetry install 
poetry run pyinstaller main.py
cp .\config.json .\dist\main
cp -r .\assets .\dist\main
mkdir -p .\dist\main\utils\desk_manager
cp .\utils\desk_manager\VirtualDesktopAccessor.dll .\dist\main\utils\desk_manager\
```

# Attribution

- Tray Icons: by [Yusuke Kamiyamane](http://p.yusukekamiyamane.com/). Licensed under
  a [Creative Commons Attribution 3.0 License](http://creativecommons.org/licenses/by/3.0/).
- The `utils/desk_manager` subpackage make use of `VirtualDesktopAccessor.dll` create
  by [Jari Pennanen](https://github.com/Ciantic)
  