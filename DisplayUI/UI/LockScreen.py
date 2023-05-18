
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

import requests

import shared
from UI.MainScreen import Main
from UI.Navigating import Navigating

class LockScreen(QMainWindow):

    childClosed = pyqtSignal()

    def __init__(self):
        super().__init__()
        loadUi("UI/LockScreen.ui", self)
        self.toReturn = False
        self.initUI()

        self.wu = Main(self.childClosed)
        self.na = Navigating()

    def initUI(self):
        shared.cmd_thr.reached.connect(self.openWaitingUser)
        shared.cmd_thr.navigating.connect(self.openNavigating)

        self.curr_time_timer = QTimer()
        self.curr_time_timer.setInterval(1000)
        self.curr_time_timer.timeout.connect(self.showCurrTime)
        self.curr_time_timer.start()
        self.showCurrTime()

        self.childClosed.connect(self.checkPending)
        shared.cmd_thr.departure.connect(self.checkPending)
        self.departure_timer = QTimer()
        self.departure_timer.setInterval(1000)
        self.departure_timer.timeout.connect(self.countDepartureTimer)

        # shared.cmd_thr.openBox.connect(self.openBoxDialogue)
        
        return
    
    def mouseReleaseEvent(self, e):
        self.departure_timer.stop()
        self.delivery_notice.setText("")
        self.main = Main(self.childClosed)
        shared.stack.addWidget(self.main)
        shared.stack.setCurrentWidget(self.main)

    def openWaitingUser(self):
        shared.stack.addWidget(self.wu)
        shared.stack.setCurrentWidget(self.wu)

    def openNavigating(self):
        shared.stack.addWidget(self.na)
        shared.stack.setCurrentWidget(self.na)

    # @QtCore.pyqtSlot(int)
    # def openBoxDialogue(self, msg):
    #     self.bd = BoxDialogue(msg)
    #     shared.stack.addWidget(self.bd)
    #     shared.stack.setCurrentWidget(self.bd)

    def showCurrTime(self):
        time = QTime.currentTime()
        self.time_label.setText(time.toString('AP hh:mm:ss'))

    def checkPending(self):
        r = requests.get("http://10.8.0.1:5000/op/pending")
        data = r.json()
        if (data['isPending']):
            self.toReturn = False
            self.departure_timeout = 10
            self.departure_timer.start()
        elif(not data['inDefaultPosition']):
            self.toReturn = True
            self.departure_timeout = 10
            self.departure_timer.start()


    def countDepartureTimer(self):
        self.departure_timeout -= 1
        if(self.departure_timeout == 0):
            self.departure_timer.stop()
            self.delivery_notice.setText("")
            if self.toReturn:
                requests.post("http://10.8.0.1:5000/op/returnDefaultPosition")
            else:
                requests.post("http://10.8.0.1:5000/op/makeGoal")
            return
        
        self.delivery_notice.setText(str(self.departure_timeout) + "초 후 로봇이 출발합니다...")
