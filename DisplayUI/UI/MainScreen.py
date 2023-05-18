
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

import shared
import requests
import json

from UI.SendDoc import SendDoc
from UI.Devtools import DevTools
from UI.AuthMethods import AuthMethods

class Main(QMainWindow):


    childClosed = pyqtSignal()

    def __init__(self, signal):
        super().__init__()
        loadUi("UI/MainScreen.ui", self)
        self.initUI()
        self.closeSignal = signal

    def initUI(self):
        shared.noInput.tickSecond.connect(self.countSecond)
        shared.noInput.elapsed.connect(self.close)
        shared.noInput.startTimer()
        self.countSecond()
        
        self.dev_button.clicked.connect(self.openDevTools)
        self.send_doc_button.clicked.connect(self.openSendDoc)
        self.recv_doc_button.clicked.connect(self.openAuthMethods)
        self.back_button.clicked.connect(self.close)
        requests.post("http://10.8.0.1:5000/op/userOccupation")

    def countSecond(self):
        timeLeft = shared.noInput.timeLeft
        min = str(timeLeft // 60).zfill(2)
        sec = str(timeLeft % 60).zfill(2)
        self.timeout_timer.setText("잔여 시간 : " + min + "분 " + sec + "초")
    
    def openSendDoc(self):
        self.sd = SendDoc()
        shared.stack.addWidget(self.sd)
        shared.stack.setCurrentWidget(self.sd)
        
    def openAuthMethods(self):
        self.am = AuthMethods()
        shared.stack.addWidget(self.am)
        shared.stack.setCurrentWidget(self.am)

    def openDevTools(self):
        self.dev = DevTools()
        shared.stack.addWidget(self.dev)
        shared.stack.setCurrentWidget(self.dev)

    def close(self):
        shared.noInput.stopTimer()
        requests.delete("http://10.8.0.1:5000/op/userOccupation")
        self.closeSignal.emit()
        shared.stack.removeWidget(self)