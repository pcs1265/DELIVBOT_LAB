from flask import Flask, jsonify, request

import base64
import numpy as np
import cv2
import pickle

import dlib

detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('models/dlib_face_recognition_resnet_model_v1.dat')

def find_faces(img):
    dets = detector(img, 1)

    if len(dets) == 0:
        return np.empty(0), np.empty(0), np.empty(0)
    
    rects, shapes = [], []
    shapes_np = np.zeros((len(dets), 68, 2), dtype=np.int32)
    for k, d in enumerate(dets):
        rect = ((d.left(), d.top()), (d.right(), d.bottom()))
        rects.append(rect)

        shape = sp(img, d)

        for i in range(0, 68):
            shapes_np[k][i] = (shape.part(i).x, shape.part(i).y)

        shapes.append(shape)

    return rects, shapes, shapes_np

def encode_faces(img, shapes):
    face_descriptors = []
    for shape in shapes:
        face_chip = dlib.get_face_chip(img, shape)
        face_descriptor = facerec.compute_face_descriptor(face_chip)
        face_descriptors.append(np.array(face_descriptor))
    
    return face_descriptors


with open("data/face.dat", "rb") as facedata:
    descs = pickle.load(facedata)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def visit():

    if request.method == 'POST':
        data = request.get_json()
        data = base64.b64decode(data['img'])

        jpg_arr = np.frombuffer(data, dtype=np.uint8)
        img_bgr = cv2.imdecode(jpg_arr, cv2.IMREAD_COLOR)

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        rects, shapes, _ = find_faces(img_rgb)
        descriptors = encode_faces(img_rgb, shapes)

        response = {'found': False, 'name': 'none', 'dist': 0.6}

        for i, desc in enumerate(descriptors):
            last_found = {'name': 'unknown', 'dist': 0.6}

            for name, saved_desc in descs.items():
                dist = float(np.linalg.norm([desc] - saved_desc, axis=1))
                
                if dist < last_found['dist']:
                    last_found = {'name': name, 'dist': dist}
                    response = {'found': False, 'name': 'none', 'dist': 0.6}
                    response['name'] = name
                    response['dist'] = dist
        return response

app.run(host = '0.0.0.0', port=8080, threaded=False)
