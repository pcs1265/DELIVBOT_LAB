
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

import shared
import requests

from UI.SendDoc import SendDoc
from UI.ScanFace import ScanFace
from UI.Devtools import DevTools

class Main(QMainWindow):

    def __init__(self, signal):
        super().__init__()
        self.closeSignal = signal
        loadUi("UI/MainScreen.ui", self)
        self.initUI()

    def initUI(self):
        self.dev_button.clicked.connect(self.openDevTools)
        self.send_doc_button.clicked.connect(self.openSendDoc)
        self.recv_doc_button.clicked.connect(self.openRecvDoc)
        self.back_button.clicked.connect(self.close)

    def openDevTools(self):
        self.dev = DevTools()
        shared.stack.addWidget(self.dev)
        shared.stack.setCurrentWidget(self.dev)

    def openSendDoc(self):
        self.sd = SendDoc()
        shared.stack.addWidget(self.sd)
        shared.stack.setCurrentWidget(self.sd)
        
    def openRecvDoc(self):
        self.sf = ScanFace()
        shared.stack.addWidget(self.sf)
        shared.stack.setCurrentWidget(self.sf)

    def close(self):
        self.closeSignal.emit()
        shared.stack.removeWidget(self)

