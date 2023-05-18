from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

from threading import Thread

import pyrealsense2 as rs
import dlib
import numpy as np
import cv2
import json
import time 

import requests
from enum import IntEnum
import shared
from UI.RecvComplete import RecvComplete


class ScanQR(QMainWindow):

    scanTick = pyqtSignal()

    def __init__(self):
        super().__init__()
        loadUi("UI/ScanQR.ui", self)
        self.initUI()
        self.last_id = None
        self.last_time = None
        self.last_name = None
        self.lasting = False
        

    def initUI(self):
        shared.noInput.tickSecond.connect(self.countSecond)
        shared.noInput.elapsed.connect(self.close)
        shared.noInput.startTimer()
        self.countSecond()
        
        self.scanTick.connect(self.updateButton)

        self.back_button.clicked.connect(self.close)
        self.auth_button.clicked.connect(lambda:self.openRecvComplete())
        self.auth_button.setVisible(False)
        
        self.th = ScanQRThread(self, self.status_text)
        self.th.start()
        return
    
    def countSecond(self):
        timeLeft = shared.noInput.timeLeft
        min = str(timeLeft // 60).zfill(2)
        sec = str(timeLeft % 60).zfill(2)
        self.timeout_timer.setText("잔여 시간 : " + min + "분 " + sec + "초")

    def openRecvComplete(self):
        self.rc = RecvComplete(self.last_id, self.last_name)
        shared.stack.addWidget(self.rc)
        shared.stack.setCurrentWidget(self.rc)
        self.close()

        
    def updateButton(self):
        currTime = time.time()
        if(self.result["found"]):
            self.lasting = True
            self.last_time = currTime
            if(self.result["matched"]):
                self.last_id = self.result["id"]
                self.last_name = self.result["name"]

                self.title.setText(self.last_name + "님 환영합니다.")
                self.auth_button.setVisible(True)
            else:
                self.title.setText("유효하지 않은 QR코드입니다.")
                self.auth_button.setVisible(False)

        
        if(self.lasting and currTime - self.last_time > 5):
            self.title.setText("카메라에 수령용 QR코드를 비춰주세요.")
            self.auth_button.setVisible(False)
            self.lasting = False
        return

    def close(self):
        self.th.stop()
        shared.noInput.startTimer()
        shared.stack.removeWidget(self)

class ScanQRThread(QThread):

    def __init__(self, parent, comment): 
    	# main에서 받은 self인자를 parent로 생성
        super().__init__(parent)        
        self.parent = parent     
        self.comment = comment
        self.last_auth = time.time()

    def run(self):
        self.working = True

        align_to_color = rs.align( rs.stream.color )
        good_color = ( 0, 255, 0 )

        while self.working :
            data = shared.pipe.wait_for_frames(); # Wait for next set of frames from the camera
            data = align_to_color.process( data )       # Replace with aligned frames
            depth_frame = data.get_depth_frame()
            color_frame = data.get_color_frame()

            # Create a dlib image for face detection
            image = np.asanyarray(color_frame.get_data())
            qr = cv2.QRCodeDetector()

            data, box, straight_qrcode = qr.detectAndDecode(image)
            
            result = {"found": False, "matched": False}

            if (data):
                lefttop = int(box[0][0][0]), int(box[0][0][1])
                leftbottom = int(box[0][1][0]), int(box[0][1][1])
                rightbottom = int(box[0][2][0]), int(box[0][2][1])
                righttop = int(box[0][3][0]), int(box[0][3][1])
                
                cv2.line(image, lefttop, leftbottom, color=good_color, thickness=10)
                cv2.line(image, lefttop, righttop, color=good_color, thickness=10)
                cv2.line(image, rightbottom, leftbottom, color=good_color, thickness=10)
                cv2.line(image, rightbottom, righttop, color=good_color, thickness=10)
                
                if(time.time() - self.last_auth > 0.5):
                    self.last_auth = time.time()
                    headers = {'Content-Type': 'application/json; chearset=utf-8'}
                    qr_data = {'QR': str(data)}
                    qr_data = json.dumps(qr_data)
                    try:
                        response = requests.post('http://10.8.0.1:8080/QRAuth', data=qr_data, headers=headers)
                        result = response.json()
                        result['found'] = True

                    except:
                        self.comment.setText("서버에 연결할 수 없습니다.")
                
                
            self.parent.result = result
            self.parent.scanTick.emit()
            
            image = cv2.flip(image, 1)
            h,w,c = image.shape

            qImg = QtGui.QImage(image, w, h, w*c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.parent.camera.setPixmap(pixmap)

    def stop(self):
        self.working = False
        self.quit()

