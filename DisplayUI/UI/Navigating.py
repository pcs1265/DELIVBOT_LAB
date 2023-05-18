from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from threading import Thread

import shared
import requests
import json

class Navigating(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("UI/Navigating.ui", self)

        self.initUI()

    def initUI(self):

        shared.cmd_thr.returned.connect(self.close)
        return
    
    def close(self):
        shared.stack.removeWidget(self)
