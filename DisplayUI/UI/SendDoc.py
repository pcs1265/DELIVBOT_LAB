from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

import shared

class SendDoc(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("UI/SendDoc.ui", self)
        self.initUI()

    def initUI(self):
        self.back_button.clicked.connect(self.close)
        pixmap = QtGui.QPixmap('UI/img/qr.png')
        self.QRImage.setPixmap(pixmap)
        self.QRImage.show()
    
    def close(self):
        shared.stack.removeWidget(self)