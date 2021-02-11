# Intro

TODO

# Demo

TODO

# Docs

TODO

# Links

- VirtualDesktopAccessor: https://github.com/Ciantic/VirtualDesktopAccessor

## Docs

- System Tray: https://www.learnpyqt.com/tutorials/system-tray-mac-menu-bar-applications-pyqt/
- QInputDialog: https://doc.qt.io/qt-5/qinputdialog.html
- PyInstaller usage: https://pyinstaller.readthedocs.io/en/stable/usage.html

## Tutorials

- Packaging: https://www.learnpyqt.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/

# Packaging

Make sure you have [`poetry`](https://python-poetry.org/) and [`yarn`](https://yarnpkg.com/) installed. In the project
directory execute:

```powershell
poetry install
 
cd web/frontend/
yarn install
yarn build

cd ../..
poetry run pyinstaller quick_task_switcher.spec
```

Then open the `Quick Task Switcher.exe` under `dist\Quick Task Switcher`. To generate single binary file use
the `quick_task_switcher_onefile.spec` instead.

# Attribution

- Tray Icons: by [Yusuke Kamiyamane](http://p.yusukekamiyamane.com/). Licensed under
  a [Creative Commons Attribution 3.0 License](http://creativecommons.org/licenses/by/3.0/).
- The `utils/desk_manager` subpackage make use of `VirtualDesktopAccessor.dll` create
  by [Jari Pennanen](https://github.com/Ciantic)
