
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

import shared
import requests
import json

from UI.ScanQR import ScanQR
from UI.ScanFace import ScanFace

class AuthMethods(QMainWindow):


    def __init__(self):
        super().__init__()
        loadUi("UI/AuthMethods.ui", self)
        self.initUI()

    def initUI(self):
        shared.noInput.tickSecond.connect(self.countSecond)
        shared.noInput.elapsed.connect(self.close)
        shared.noInput.startTimer()
        self.countSecond()

        self.qr_button.clicked.connect(self.openScanQR)
        self.face_button.clicked.connect(self.openScanFace)
        self.back_button.clicked.connect(self.close)

    def countSecond(self):
        timeLeft = shared.noInput.timeLeft
        min = str(timeLeft // 60).zfill(2)
        sec = str(timeLeft % 60).zfill(2)
        self.timeout_timer.setText("잔여 시간 : " + min + "분 " + sec + "초")
    
    def openScanQR(self):
        self.sq = ScanQR()
        shared.stack.addWidget(self.sq)
        shared.stack.setCurrentWidget(self.sq)
        
    def openScanFace(self):
        self.sf = ScanFace()
        shared.stack.addWidget(self.sf)
        shared.stack.setCurrentWidget(self.sf)

    def close(self):
        shared.noInput.startTimer()
        shared.stack.removeWidget(self)