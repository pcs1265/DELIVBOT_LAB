## Ex 3-3. 창 닫기.

import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

#import roslibpy
import json

from UI.LockScreen import LockScreen

def robot_cmd_recv(f):
        global cmd
        jsonString = f['data']
        cmd = json.loads(jsonString)
        if(cmd['cmd_code'] == 0):
            print('도착')
            lock.reached.emit()
        elif(cmd['cmd_code'] == 1):
            print('카운트 시작')
            lock.departure.emit()

def initialize():

    global cmd
    global app
    app = QApplication(sys.argv)
    
    global stack
    stack = QStackedWidget()

    global lock