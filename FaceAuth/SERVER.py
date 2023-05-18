from flask import Flask, jsonify, request

import pymysql
import base64
import numpy as np
import cv2
import pickle

from datetime import datetime
registered_descs = {}

#DB 연결 수립
database = pymysql.connect(host='localhost', user='pcs1265', password='#cs000218',db='robotLAB', charset='utf8')


def loadAllFaceDesc():
    # 데이터베이스 커서 생성
    cur = database.cursor()

    # SQL Delivery 규칙
    # 0 : 배달대기
    # 1 : 배달중
    # 2 : 유기
    # 3 : 배달완료
    sql = "SELECT u.user_id, u.name, u.face_desc " \
          "FROM user_table u"
    
    # SQL문 실행
    cur.execute(sql)
    
    # 실행된 결과 가져오기
    rows = cur.fetchall()

    loaded_face_descs = {}

    for row in rows:
        id = row[0]
        name = row[1]
        face_desc_str = row[2]

        face_desc = None
        if(face_desc_str != None):
            face_desc_byte = base64.decodebytes(face_desc_str.encode('ascii'))
            face_desc = np.frombuffer(face_desc_byte, dtype=np.float64)
            loaded_face_descs[id] = (name, face_desc)
        

    global registered_descs
    registered_descs = loaded_face_descs
    # 데이터베이스 커밋
    database.commit()

    return

loadAllFaceDesc()
print(registered_descs)

# with open("data/face.dat", "rb") as facedata:
#     registered_descs = pickle.load(facedata)

app = Flask(__name__)

def storedUserFaceDesc():
    # 데이터베이스 커서 생성
    cur = database.cursor()

    # SQL Delivery 규칙
    # 0 : 배달대기
    # 1 : 배달중
    # 2 : 유기
    # 3 : 배달완료
    sql = "SELECT u.user_id, u.name, u.face_desc " \
          "FROM user_table u " \
          "JOIN user_table u ON d.receive_userid = u.user_id " \
          "WHERE d.status = 0"
    
    # SQL문 실행
    cur.execute(sql)
    
    # 실행된 결과 가져오기
    rows = cur.fetchall()
    
    # 데이터베이스 커밋
    database.commit()

    return

@app.route('/faceAuth', methods=['POST'])
def faceAuth():
        
    data = request.get_json()

    captured_desc = np.array(data['desc'], dtype=np.float64)
    
    response = {"matched" :False}

    min_dist = 1
    min_dist_id = None

    for r_id in registered_descs:
        dist = np.linalg.norm(captured_desc - registered_descs[r_id][1], axis=0)
        if dist < min_dist:
            min_dist = dist
            min_dist_id = r_id
    
    if min_dist < 0.4:
        response['matched'] = True
        response['id'] = min_dist_id
        response['name'] = registered_descs[min_dist_id][0]
    
    return response

@app.route('/updateDB', methods=['POST'])
def updateDB():

    loadAllFaceDesc()
    return ""

@app.route('/QRAuth', methods=['POST'])
def QRAuth():
        
    data = request.get_json()

    qr_data = data['QR']
    
    response = {"matched" :False}

    # 데이터베이스 커서 생성
    cur = database.cursor()

    # SQL Delivery 규칙
    # 0 : 배달대기
    # 1 : 배달중
    # 2 : 유기
    # 3 : 배달완료
    sql = "SELECT u.user_id, u.name, u.qr_time " \
          "FROM user_table u " \
          "WHERE user_qr = \"" + qr_data + "\""
    
    # SQL문 실행
    cur.execute(sql)
    
    # 실행된 결과 가져오기
    rows = cur.fetchall()
    
    # 데이터베이스 커밋
    database.commit()

    
    if len(rows) != 0:
        qr_time = rows[0][2]
        if (datetime.now() - qr_time).seconds < 300:
            response['matched'] = True
            response['id'] = rows[0][0]
            response['name'] = rows[0][1]
    return response


app.run(host = '0.0.0.0', port=8080, threaded=True)
