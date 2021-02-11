from PyQt5 import QtWidgets, QtCore, QtWebEngineWidgets

from utils.paths import resource_path


class WebWindow(QtWidgets.QMainWindow):

    def __init__(self, parent):
        super(WebWindow, self).__init__(parent)

        self.browser = QtWebEngineWidgets.QWebEngineView()

        # load frontend
        frontend_url = QtCore.QUrl.fromLocalFile(resource_path('./web/frontend/dist/index.html'))
        self.browser.setUrl(frontend_url)

        # set title
        self.setWindowTitle('Quick Task Switcher: Web Interface')

        self.setCentralWidget(self.browser)

    def reload_and_show(self):
        self.browser.reload()
        self.show()
