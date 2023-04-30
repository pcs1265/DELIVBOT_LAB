from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from threading import Thread

import pyrealsense2 as rs
import dlib
import numpy as np
from enum import IntEnum
import shared


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

def find_depth_from(frame, depth_scale, face, markup_from, markup_to, p_average_depth):
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

def validate_face(frame, depth_scale, face):
    # Collect all the depth information for the different facial parts

    # For the ears, only one may be visible -- we take the closer one!
    left_ear_depth = 100
    right_ear_depth = 100
    
    t1, right_ear_depth = find_depth_from( frame, depth_scale, face, markup_68.RIGHT_EAR, markup_68.RIGHT_1, right_ear_depth )
    t2, left_ear_depth = find_depth_from( frame, depth_scale, face, markup_68.LEFT_1, markup_68.LEFT_EAR, left_ear_depth )
    if( (not t1) and (not t2) ):
        return False
    ear_depth = min( right_ear_depth, left_ear_depth )

    t1, chin_depth = find_depth_from( frame, depth_scale, face, markup_68.CHIN_FROM, markup_68.CHIN_TO, 0 )
    if( (not t1) ):
        return False

    t1, nose_depth = find_depth_from( frame, depth_scale, face, markup_68.NOSE_TIP, markup_68.NOSE_TIP, 0 )
    if( (not t1) ):
        return False

    t1, right_eye_depth = find_depth_from( frame, depth_scale, face, markup_68.RIGHT_EYE_FROM, markup_68.RIGHT_EYE_TO, 0)
    if( (not t1) ):
        return False
    
    t1, left_eye_depth = find_depth_from( frame, depth_scale, face, markup_68.LEFT_EYE_FROM, markup_68.LEFT_EYE_TO, 0 ) 
    if( (not t1) ):
        return False

    eye_depth = min( left_eye_depth, right_eye_depth )

    t1, mouth_depth = find_depth_from( frame, depth_scale, face, markup_68.MOUTH_OUTER_FROM, markup_68.MOUTH_INNER_TO, 0 )
    if( (not t1) ):
        return False

    # // We just use simple heuristics to determine whether the depth information agrees with
    # // what's expected: that the nose tip, for example, should be closer to the camera than
    # // the eyes.

    # // These heuristics are fairly basic but nonetheless serve to illustrate the point that
    # // depth data can effectively be used to distinguish between a person and a picture of a
    # // person...

    # print("nose", nose_depth)
    # print("eye", eye_depth)
    # print("ear", ear_depth)
    # print("mouth", mouth_depth)
    # print("chin", chin_depth)

    if( nose_depth >= eye_depth ):
        return False
    if( eye_depth - nose_depth > 0.1 ):
        return False
    # if( ear_depth <= eye_depth ):
    #     return False
    if( mouth_depth <= nose_depth ):
        return False
    if( mouth_depth > chin_depth ):
        return False

    # // All the distances, collectively, should not span a range that makes no sense. I.e.,
    # // if the face accounts for more than 20cm of depth, or less than 2cm, then something's
    # // not kosher!

    x = max( { nose_depth, eye_depth, ear_depth, mouth_depth, chin_depth } )
    n = min( { nose_depth, eye_depth, ear_depth, mouth_depth, chin_depth } )


    if( x - n > 0.20 ):
        return False
    if( x - n < 0.01 ):
        return False

    return True



class ScanFace(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("UI/ScanFace.ui", self)
        self.initUI()

    def initUI(self):
        self.back_button.clicked.connect(self.close)
        
        self.running = True
        self.th = Thread(target=runCamera, args=(self, ))
        self.th.start()
        return
        
    
    def close(self):
        self.running = False
        self.th.join()
        shared.stack.removeWidget(self)


def runCamera(widget):
    pipe = rs.pipeline()

    # Configure streams
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
    profile = pipe.start(config)

    # Each depth camera might have different units for depth pixels, so we get it here
    # Using the pipeline's profile, we can retrieve the device that the pipeline uses
    DEPTH_SENSOR = profile.get_device().first_depth_sensor()
    DEVICE_DEPTH_SCALE = DEPTH_SENSOR.get_depth_scale()
    print(DEVICE_DEPTH_SCALE)
    
    face_bbox_detector = dlib.get_frontal_face_detector()
    #face_bbox_detector = dlib.cnn_face_detection_model_v1("mmod_human_face_detector.dat")
    face_landmark_annotator = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    align_to_color = rs.align( rs.stream.color )
    bad_color = dlib.rgb_pixel( 255, 0, 0 )
    good_color = dlib.rgb_pixel( 0, 255, 0 )

    while widget.running:
        data = pipe.wait_for_frames(); # Wait for next set of frames from the camera
        data = align_to_color.process( data )       # Replace with aligned frames
        depth_frame = data.get_depth_frame()
        color_frame = data.get_color_frame()
        
        #print(depth_frame.get_distance(320, 240))

        # Create a dlib image for face detection
        image = np.asanyarray(color_frame.get_data())

        # Detect faces: find bounding boxes around all faces, then annotate each to find its landmarks
        face_bboxes = face_bbox_detector( image )
        faces = []
        for bbox in face_bboxes:

            faces.append( face_landmark_annotator( image, bbox ))

        color_image = np.asanyarray(color_frame.get_data())
        h,w,c = color_image.shape
        qImg = QtGui.QImage(color_image, w, h, w*c, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        widget.camera.setPixmap(pixmap)

    return