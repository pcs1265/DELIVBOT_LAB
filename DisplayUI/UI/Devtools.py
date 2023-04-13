
from PyQt5.QtWidgets import *

from PyQt5.QtCore import *
from PyQt5.uic import loadUi

import shared

class DevTools(QMainWindow):

    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        loadUi("UI/DevTools.ui", self)
        self.initUI()


    def initUI(self):
        self.quit_button.clicked.connect(QCoreApplication.instance().quit)
        self.exit_dev_button.clicked.connect(self.close)

        self.statusBar().showMessage('DevTools')

    def close(self):
        shared.stack.removeWidget(self)
