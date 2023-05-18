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



class markup_68(IntEnum):
    # Starting with right ear, the jaw [1-17]
    RIGHT_EAR = 0,
    JAW_FROM = 0,
    RIGHT_JAW_FROM = 0,
    RIGHT_1 = 1,
    RIGHT_2 = 2,
    RIGHT_3 = 3, 
    RIGHT_4 = 4, 
    RIGHT_5 = 5, 
    RIGHT_6 = 6, 
    RIGHT_7 = 7,
    RIGHT_JAW_TO = 7,
    CHIN = 8,
    CHIN_FROM = 7,
    CHIN_TO = 9,
    LEFT_7 = 9,
    LEFT_JAW_FROM = 9,
    LEFT_6 = 10,
    LEFT_5 = 11,
    LEFT_4 = 12,
    LEFT_3 = 13,
    LEFT_2 = 14,
    LEFT_1 = 15,
    LEFT_EAR = 16,
    LEFT_JAW_TO = 16,
    JAW_TO = 16,

    # Eyebrows [18-22] and [23-27]
    RIGHT_EYEBROW_R = 17,
    RIGHT_EYEBROW_FROM = 17,
    RIGHT_EYEBROW_1 = 18,
    RIGHT_EYEBROW_2 = 19,
    RIGHT_EYEBROW_3 = 20,
    RIGHT_EYEBROW_L = 21,
    RIGHT_EYEBROW_TO = 21,
    LEFT_EYEBROW_R = 22,
    LEFT_EYEBROW_FROM = 22,
    LEFT_EYEBROW_1 = 23,
    LEFT_EYEBROW_2 = 24,
    LEFT_EYEBROW_3 = 25,
    LEFT_EYEBROW_L = 26,
    LEFT_EYEBROW_TO = 26,

    # Nose [28-36]
    NOSE_RIDGE_TOP = 27,
    NOSE_RIDGE_FROM = 27,
    NOSE_RIDGE_1 = 28,
    NOSE_RIDGE_2 = 29,
    NOSE_TIP = 30,
    NOSE_RIDGE_TO = 30,
    NOSE_BOTTOM_R = 31,
    NOSE_BOTTOM_FROM = 31,
    NOSE_BOTTOM_1 = 32,
    NOSE_BOTTOM_2 = 33,
    NOSE_BOTTOM_3 = 34,
    NOSE_BOTTOM_L = 35,
    NOSE_BOTTOM_TO = 35,

    # Eyes [37-42] and [43-48]
    RIGHT_EYE_R = 36,
    RIGHT_EYE_FROM = 36,
    RIGHT_EYE_1 = 37,
    RIGHT_EYE_2 = 38,
    RIGHT_EYE_L = 39,
    RIGHT_EYE_4 = 40,
    RIGHT_EYE_5 = 41,
    RIGHT_EYE_TO = 41,
    LEFT_EYE_R = 42,
    LEFT_EYE_FROM = 42,
    LEFT_EYE_1 = 43,
    LEFT_EYE_2 = 44,
    LEFT_EYE_L = 45,
    LEFT_EYE_4 = 46,
    LEFT_EYE_5 = 47,
    LEFT_EYE_TO = 47,

    # Mouth [49-68]
    MOUTH_R = 48,
    MOUTH_OUTER_R = 48,
    MOUTH_OUTER_FROM = 48,
    MOUTH_OUTER_1 = 49,
    MOUTH_OUTER_2 = 50,
    MOUTH_OUTER_TOP = 51,
    MOUTH_OUTER_4 = 52,
    MOUTH_OUTER_5 = 53,
    MOUTH_L = 54,
    MOUTH_OUTER_L = 54,
    MOUTH_OUTER_7 = 55,
    MOUTH_OUTER_8 = 56,
    MOUTH_OUTER_BOTTOM = 57,
    MOUTH_OUTER_10 = 58,
    MOUTH_OUTER_11 = 59,
    MOUTH_OUTER_TO = 59,
    MOUTH_INNER_R = 60,
    MOUTH_INNER_FROM = 60,
    MOUTH_INNER_1 = 61,
    MOUTH_INNER_TOP = 62,
    MOUTH_INNER_3 = 63,
    MOUTH_INNER_L = 64,
    MOUTH_INNER_5 = 65,
    MOUTH_INNER_BOTTOM = 66,
    MOUTH_INNER_7 = 67,
    MOUTH_INNER_TO = 67,

    N_POINTS = 68

def find_depth_from(frame, face, markup_from, markup_to, p_average_depth):
    average_depth = 0
    n_points = 0
    for i in range(markup_from, markup_to+1):
        pt = face.part( i )
        if( pt.x <= 0 or pt.x >= frame.get_width() or pt.y <= 0 or pt.y >= frame.get_height() ):
             continue
        depth_in_pixels = frame.get_distance(pt.x, pt.y)
        average_depth += depth_in_pixels
        n_points += 1
    if( n_points == 0 ):
        return False, p_average_depth
    p_average_depth = average_depth / n_points
    return True, p_average_depth

def validate_face(frame, face):
    # Collect all the depth information for the different facial parts

    # For the ears, only one may be visible -- we take the closer one!
    left_ear_depth = 100
    right_ear_depth = 100
    
    t1, right_ear_depth = find_depth_from( frame, face, markup_68.RIGHT_EAR, markup_68.RIGHT_1, right_ear_depth )
    t2, left_ear_depth = find_depth_from( frame, face, markup_68.LEFT_1, markup_68.LEFT_EAR, left_ear_depth )
    if( (not t1) and (not t2) ):
        return False
    ear_depth = min( right_ear_depth, left_ear_depth )

    t1, chin_depth = find_depth_from( frame, face, markup_68.CHIN_FROM, markup_68.CHIN_TO, 0 )
    if( (not t1) ):
        return False

    t1, nose_depth = find_depth_from( frame, face, markup_68.NOSE_TIP, markup_68.NOSE_TIP, 0 )
    if( (not t1) ):
        return False

    t1, right_eye_depth = find_depth_from( frame, face, markup_68.RIGHT_EYE_FROM, markup_68.RIGHT_EYE_TO, 0)
    if( (not t1) ):
        return False
    
    t1, left_eye_depth = find_depth_from( frame, face, markup_68.LEFT_EYE_FROM, markup_68.LEFT_EYE_TO, 0 ) 
    if( (not t1) ):
        return False

    eye_depth = min( left_eye_depth, right_eye_depth )

    t1, mouth_depth = find_depth_from( frame, face, markup_68.MOUTH_OUTER_FROM, markup_68.MOUTH_INNER_TO, 0 )
    if( (not t1) ):
        return False

    # // We just use simple heuristics to determine whether the depth information agrees with
    # // what's expected: that the nose tip, for example, should be closer to the camera than
    # // the eyes.

    # // These heuristics are fairly basic but nonetheless serve to illustrate the point that
    # // depth data can effectively be used to distinguish between a person and a picture of a
    # // person...

    if( nose_depth >= eye_depth ):
        return False
    if( eye_depth - nose_depth > 0.2 ):
        return False
    # if( ear_depth <= eye_depth ):
    #     return False
    if( mouth_depth <= nose_depth ):
        return False
    #if( mouth_depth > chin_depth ):
    #    return False

    # // All the distances, collectively, should not span a range that makes no sense. I.e.,
    # // if the face accounts for more than 20cm of depth, or less than 2cm, then something's
    # // not kosher!

    x = max( { nose_depth, eye_depth, mouth_depth, chin_depth } )
    n = min( { nose_depth, eye_depth, mouth_depth, chin_depth } )

    if( x - n > 0.20 ):
        return False
    if( x - n < 0.02 ):
        return False

    return True

def draw(image, face, color):
    for i in range(0, 68):
        pt = face.part(i)
        image = cv2.circle(image, center=(pt.x, pt.y), radius=1, color=color, thickness=-1)
    return image

class ScanFace(QMainWindow):

    scanTick = pyqtSignal()

    def __init__(self):
        super().__init__()
        loadUi("UI/ScanFace.ui", self)
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
        
        self.th = ScanFaceThread(self, self.status_text)
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
        self.th.stop()
        shared.noInput.stopTimer()
        shared.stack.removeWidget(self)

        
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
                self.title.setText("식별할 수 없는 사용자입니다.")
                self.auth_button.setVisible(False)

        
        if(self.lasting and currTime - self.last_time > 5):
            self.title.setText("카메라에 얼굴을 비춰주세요.")
            self.auth_button.setVisible(False)
            self.lasting = False
        return

    def close(self):
        self.th.stop()
        shared.noInput.startTimer()
        shared.stack.removeWidget(self)

def encode_faces(img, faces):
    face_descriptors = []
    for face in faces:
        face_chip = dlib.get_face_chip(img, face)
        face_descriptor = shared.face_recognition_model.compute_face_descriptor(face_chip)
        face_descriptors.append(np.array(face_descriptor).tolist())
    return face_descriptors

def encode_face(img, face):
        face_chip = dlib.get_face_chip(img, face)
        face_descriptor = shared.face_recognition_model.compute_face_descriptor(face_chip)
        face_descriptor = np.array(face_descriptor).tolist()
        return face_descriptor

def getNearestFace(frame, faces):
    nearest_depth = 987654321
    nearest_face = None
    for face in faces:
        t1, curr_depth = find_depth_from( frame, face, markup_68.NOSE_TIP, markup_68.NOSE_TIP, 0 )
        if nearest_depth > curr_depth:
            nearest_depth = curr_depth
            nearest_face = face
    return nearest_face

class ScanFaceThread(QThread):

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

            # Detect faces: find bounding boxes around all faces, then annotate each to find its landmarks
            face_bboxes = shared.face_bbox_detector( image )
            faces = []
            for bbox in face_bboxes:
                faces.append( shared.face_landmark_annotator( image, bbox ))
            
            valid_faces = []

            for face in faces:
                if validate_face(depth_frame, face):
                    valid_faces.append(face)


            nearest_face = getNearestFace(depth_frame, valid_faces)

            result = {"found": False, "matched": False}

            if(nearest_face != None and time.time() - self.last_auth > 0.5):
                
                self.last_auth = time.time()
                enc_face = encode_face(image, nearest_face)
                headers = {'Content-Type': 'application/json; chearset=utf-8'}
                face_desc = {'desc':enc_face}
                face_desc = json.dumps(face_desc)
                try:
                    response = requests.post('http://10.8.0.1:8080/faceAuth', data=face_desc, headers=headers)
                    result = response.json()
                    result['found'] = True
                    self.comment.setText("")
                except:
                    self.comment.setText("서버에 연결할 수 없습니다.")
            
            self.parent.result = result
            self.parent.scanTick.emit()
            for vface in valid_faces:
                image = draw(image, vface, good_color)
            
            image = cv2.flip(image, 1)
            h,w,c = image.shape

            qImg = QtGui.QImage(image, w, h, w*c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.parent.camera.setPixmap(pixmap)

        

    def stop(self):
        self.working = False
        self.quit()

