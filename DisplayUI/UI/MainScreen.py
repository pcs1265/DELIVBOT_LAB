
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

import shared
import requests

from UI.SendDoc import SendDoc
from UI.ScanFace import ScanFace
from UI.Devtools import DevTools

class Main(QMainWindow):


    childClosed = pyqtSignal()

    def __init__(self, signal):
        super().__init__()
        loadUi("UI/MainScreen.ui", self)
        self.initUI()
        self.closeSignal = signal

    def initUI(self):
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.countSecond)
        self.startCount()

        self.dev_button.clicked.connect(self.openDevTools)
        self.send_doc_button.clicked.connect(self.openSendDoc)
        self.recv_doc_button.clicked.connect(self.openRecvDoc)
        self.back_button.clicked.connect(self.close)
        requests.post("http://10.8.0.1:5000/op/userOccupation")

    def startCount(self):
        self.timeout = 10
        self.timer.start()

    def countSecond(self):
        self.timeout -= 1
        if(self.timeout == 0):
            self.close()
        min = str(self.timeout // 60).zfill(2)
        sec = str(self.timeout % 60).zfill(2)
        self.timeout_timer.setText("잔여 시간 : " + min + "분 " + sec + "초")

    def stopCount(self):
        self.timer.stop()
        self.timeout_timer.setText("")
    
    def openSendDoc(self):
        self.stopCount()
        self.sd = SendDoc()
        shared.stack.addWidget(self.sd)
        shared.stack.setCurrentWidget(self.sd)
        
    def openRecvDoc(self):
        self.stopCount()
        self.sf = ScanFace()
        shared.stack.addWidget(self.sf)
        shared.stack.setCurrentWidget(self.sf)

    def openDevTools(self):
        self.dev = DevTools()
        shared.stack.addWidget(self.dev)
        shared.stack.setCurrentWidget(self.dev)

    def close(self):
        requests.delete("http://10.8.0.1:5000/op/userOccupation")
        self.closeSignal.emit()
        shared.stack.removeWidget(self)