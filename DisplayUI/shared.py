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
import time
import serial

import pyrealsense2 as rs

from UI.LockScreen import LockScreen


class PollThread(QThread):

    reached = pyqtSignal()
    departure = pyqtSignal()
    navigating = pyqtSignal()
    openBox = pyqtSignal(int)
    returned = pyqtSignal()

    def __init__(self, parent=None): 
    	# main에서 받은 self인자를 parent로 생성
        super().__init__(parent)        
        self.parent = parent

    def run(self):
        while True:
            try:
                r = requests.get("op/pollCommand")
                if(r.status_code == 204):
                    continue
                cmd = r.json()
                if(cmd['cmd_code'] == 0):
                    print('도착')
                    self.reached.emit()
                elif(cmd['cmd_code'] == 1):
                    print('카운트 시작')
                    self.departure.emit()
                elif(cmd['cmd_code'] == 2):
                    print('로봇 이동')
                    self.navigating.emit()
                elif(cmd['cmd_code'] == 3):
                    print('보관함 개방 :' , cmd['box'])
                    self.openBox.emit(cmd['box'])

                elif(cmd['cmd_code'] == 4):
                    print('로봇 복귀 완료')
                    self.returned.emit()

            except:
                print('로봇 커맨드 센터와 연결하지 못했습니다.')
                print('5초 후 재접속합니다', end="", flush=True)
                for i in range(5, 0, -1):
                    print('.', end="", flush=True)
                    time.sleep(1)
                print('')


NO_INPUT_TIME_LIMIT = 180

class noInputTimer(QObject):
    tickSecond = pyqtSignal()
    elapsed = pyqtSignal()
    
    def __init__(self): 
        super().__init__()
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.countSecond)
        self.timeLeft = NO_INPUT_TIME_LIMIT
        
    def startTimer(self):
        self.timeLeft = NO_INPUT_TIME_LIMIT
        if(not self.timer.isActive()):
            self.timer.start()

    def countSecond(self):
        self.timeLeft -= 1
        if(self.timeLeft == 0):
            self.timer.stop()
            self.elapsed.emit()

        self.tickSecond.emit()

    def stopTimer(self):
        if(self.timer.isActive()):
            self.timer.stop()


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

    global face_recognition_model
    face_recognition_model = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')

    global pipe
    pipe = rs.pipeline()

    global config
    # Configure streams
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
    pipe.start(config)

    global noInput
    noInput = noInputTimer()

    global boxController
    boxController = serial.Serial(port="/dev/ttyACM0", baudrate=9600)