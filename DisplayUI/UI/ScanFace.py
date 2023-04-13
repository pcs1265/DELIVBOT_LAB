from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from threading import Thread

import shared


class ScanFace(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("UI/RecvComplete.ui", self)
        self.initUI()

    def initUI(self):
        #self.back_button.clicked.connect(self.close)
        
        #self.running = True
        #self.th = Thread(target=runCamera, args=(self, ))
        #self.th.start()
        return
        
    
    def close(self):
        self.running = False
        self.th.join()
        shared.stack.removeWidget(self)


def runCamera(widget):
    # cap = cv2.VideoCapture(4)
    # while widget.running:
    #     ret, img = cap.read()
    #     if ret:
    #         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #         h,w,c = img.shape
    #         qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
    #         pixmap = QtGui.QPixmap.fromImage(qImg)
    #         widget.camera.setPixmap(pixmap)
    #     else:
    #         print("cannot read frame.")
    #         break
    # cap.release()
    return