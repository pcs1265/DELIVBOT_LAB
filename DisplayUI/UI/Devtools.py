
from PyQt5.QtWidgets import *
from PyQt5 import QtCore 
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

import shared

class DevTools(QMainWindow):

    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        loadUi("UI/DevTools.ui", self)
        self.initUI()

        self.passwd = ""
        self.passwdStar = ""
        self.unlocked = False


    def initUI(self):
        self.quit_button.setVisible(False)
        self.quit_button.clicked.connect(QCoreApplication.instance().quit)
        self.exit_dev_button.clicked.connect(self.close)
        self.pushButton_0.clicked.connect(lambda: self.inputPassword('0'))
        self.pushButton_1.clicked.connect(lambda: self.inputPassword('1'))
        self.pushButton_2.clicked.connect(lambda: self.inputPassword('2'))
        self.pushButton_3.clicked.connect(lambda: self.inputPassword('3'))
        self.pushButton_4.clicked.connect(lambda: self.inputPassword('4'))
        self.pushButton_5.clicked.connect(lambda: self.inputPassword('5'))
        self.pushButton_6.clicked.connect(lambda: self.inputPassword('6'))
        self.pushButton_7.clicked.connect(lambda: self.inputPassword('7'))
        self.pushButton_8.clicked.connect(lambda: self.inputPassword('8'))
        self.pushButton_9.clicked.connect(lambda: self.inputPassword('9'))

    ANSWER = "000218"
    
    def inputPassword(self, msg):
        if(not self.unlocked):
            self.passwd += msg
            self.passwdStar += '*'
            if(len(self.passwd) == len(self.ANSWER)):
                if(self.passwd == self.ANSWER):
                    self.unlocked = True
                    self.unlock()
                else:
                    self.passwd = ""
                    self.passwdStar = ""
            self.passwd_label.setText(self.passwdStar)

    def unlock(self):
        self.quit_button.setVisible(True)


    def close(self):
        shared.stack.removeWidget(self)
