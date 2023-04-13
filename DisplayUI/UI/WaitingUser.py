
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

import requests

import shared
from UI.ScanFace import ScanFace
from UI.SendDoc import SendDoc

class WaitingUser(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("UI/WaitingUser.ui", self)
        self.initUI()

    def initUI(self):
        self.timeout = 10
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.countSecond)
        self.timer.start()
        self.send_doc_button.clicked.connect(self.openSendDoc)
        self.recv_doc_button.clicked.connect(self.openRecvDoc)

    def countSecond(self):
        self.timeout -= 1
        if(self.timeout == 0):
            self.close()
        min = str(self.timeout // 60).zfill(2)
        sec = str(self.timeout % 60).zfill(2)
        self.timeout_timer.setText("잔여 시간 : " + min + "분 " + sec + "초")
    
    def openSendDoc(self):
        self.sd = SendDoc()
        shared.stack.addWidget(self.sd)
        shared.stack.setCurrentWidget(self.sd)
        
    def openRecvDoc(self):
        self.sf = ScanFace()
        shared.stack.addWidget(self.sf)
        shared.stack.setCurrentWidget(self.sf)

    def close(self):
        shared.stack.removeWidget(self)