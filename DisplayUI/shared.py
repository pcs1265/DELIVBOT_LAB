## Ex 3-3. 창 닫기.

import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

#import roslibpy
import json
import requests
import dlib


from UI.LockScreen import LockScreen


class PollThread(QThread):

    def __init__(self, parent=None): 
    	# main에서 받은 self인자를 parent로 생성
        super().__init__(parent)        
        self.parent = parent

    def setLockScreen(self, lock):
        self.reached = lock.reached
        self.departure = lock.departure

    def run(self):
        while True:
            r = requests.get("http://10.8.0.1:5000/op/pollCommand")
            if(r.status_code == 204):
                continue
            
            cmd = r.json()
            if(cmd['cmd_code'] == 0):
                print('도착')
                self.reached.emit()
            elif(cmd['cmd_code'] == 1):
                print('카운트 시작')
                self.departure.emit()

def initialize():

    global cmd_thr
    cmd_thr = PollThread()


    global app
    app = QApplication(sys.argv)
    
    global stack
    stack = QStackedWidget()

    global lock
    
    global face_bbox_detector
    face_bbox_detector = dlib.get_frontal_face_detector()

    #face_bbox_detector = dlib.cnn_face_detection_model_v1("mmod_human_face_detector.dat")
    
    global face_landmark_annotator
    face_landmark_annotator = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
