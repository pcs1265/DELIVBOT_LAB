from flask import Flask, jsonify, request

import base64
import numpy as np
import cv2
import pymysql
import requests

import dlib

detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('models/dlib_face_recognition_resnet_model_v1.dat')

#DB 연결 수립
database = pymysql.connect(host='localhost', user='pcs1265', password='#cs000218',db='robotLAB', charset='utf8')

def updateFaceDesc(id, desc):
    # 데이터베이스 커서 생성
    cur = database.cursor()

    sql = "UPDATE user_table " \
          "SET face_desc=\""+ desc + "\" " \
          "WHERE user_id=\"" + id + "\""
    
    # SQL문 실행
    cur.execute(sql)
    
    # 데이터베이스 커밋
    database.commit()

    return

def getFaceDesc(id):
    # 데이터베이스 커서 생성
    cur = database.cursor()

    sql = "SELECT user_id, face_desc " \
          "FROM user_table " \
          "WHERE user_id=\"" + id + "\""
    
    # SQL문 실행
    cur.execute(sql)
    
    # 실행된 결과 가져오기
    rows = cur.fetchall()

    # 데이터베이스 커밋
    database.commit()
    #print(cur.rowcount)

    result = {
        "id" : rows[0][0],
        "face_desc" : rows[0][1]
    }

    return result

def find_faces(img):
    dets = detector(img, 1)

    if len(dets) == 0:
        return [], [], []
    
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

app = Flask(__name__)
    
@app.route('/face', methods=['POST'])
def addFace():
    id = request.form["id"]
    print(id)
    file = request.files["file"]
    frame = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    rects, shapes, _ = find_faces(img_rgb)
    descriptors = encode_faces(img_rgb, shapes)

    response = {'detected':False, 'error': ""}

    if len(descriptors) != 0:
        response['detected'] = True
    if len(descriptors) >= 2:
        response['error'] = "Too many faces are detected."

    detected_face = descriptors[0]
    
    desc = base64.b64encode(detected_face).decode()

    updateFaceDesc(id, desc)
    try:
        requests.post('http://127.0.0.1:8080/updateDB')
    except:
        print("얼굴 인증 서버 갱신 요청 실패")
    
    return response

@app.route('/face', methods=['GET'])
def getFace():
    id = request.form["id"]

    result = getFaceDesc(id)
    b64_face_desc = result["face_desc"]

    r = base64.decodebytes(b64_face_desc.encode('ascii'))
    
    q = np.frombuffer(r, dtype=np.float64)

    print(q)

    return ""


app.run(host = '0.0.0.0', port=8081, threaded=False)