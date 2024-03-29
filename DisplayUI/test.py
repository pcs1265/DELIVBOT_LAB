## Ex 3-3. 창 닫기.

import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

import shared
from UI.LockScreen import LockScreen

shared.initialize()


if __name__ == '__main__':

    
    shared.lock = LockScreen()
    shared.cmd_thr.start()

    shared.stack.addWidget(shared.lock)

    monitor = QDesktopWidget().screenGeometry(1)

    shared.stack.setGeometry(monitor.left(), monitor.top(), 1024, 600)
    shared.stack.setMaximumHeight(600)
    shared.stack.setMaximumWidth(1024)
    shared.stack.showFullScreen()
    sys.exit(shared.app.exec_())