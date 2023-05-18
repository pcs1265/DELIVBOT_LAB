from flask import Flask, jsonify, request

import base64
import numpy as np
import cv2
import json
import gc

import dlib
import face_recognition

img_paths = [
    'img/duboo.png'
]

known_names = [
    'duboo'
]

encoding = []

for img_path in img_paths:
    img = face_recognition.load_image_file(img_path)

    encoding.append(face_recognition.face_encodings(img)[0])


app = Flask(__name__)

face_locations = []
face_encodings = []
face_names = []

@app.route('/', methods=['POST'])
def visit():

    if request.method == 'POST':
        data = request.get_json()
        data = base64.b64decode(data['img'])

        jpg_arr = np.frombuffer(data, dtype=np.uint8)
        img_bgr = cv2.imdecode(jpg_arr, cv2.IMREAD_COLOR)

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        response = {'name': 'none', 'dist': 0.6}


        face_locations = face_recognition.face_locations(img_rgb)
        face_encodings = face_recognition.face_encodings(img_rgb, face_locations)
        name = "Not Found"
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(encoding, face_encoding, 0.5)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(encoding, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_names[best_match_index]

        return {'name' : name}

app.run(host = '0.0.0.0', port=8080)
