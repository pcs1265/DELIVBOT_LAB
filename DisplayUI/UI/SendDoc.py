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
        shared.noInput.tickSecond.connect(self.countSecond)
        shared.noInput.elapsed.connect(self.close)
        shared.noInput.startTimer()
        self.countSecond()
        self.back_button.clicked.connect(self.close)
        pixmap = QtGui.QPixmap('UI/img/qr.png')
        self.QRImage.setPixmap(pixmap)
        self.QRImage.show()
    
    def countSecond(self):
        timeLeft = shared.noInput.timeLeft
        min = str(timeLeft // 60).zfill(2)
        sec = str(timeLeft % 60).zfill(2)
        self.timeout_timer.setText("잔여 시간 : " + min + "분 " + sec + "초")
    
    def close(self):
        shared.noInput.startTimer()
        shared.stack.removeWidget(self)