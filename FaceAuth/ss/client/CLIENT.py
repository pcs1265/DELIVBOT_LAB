import base64
import json
import requests
import cv2
import numpy as np

headers = {'Content-Type': 'application/json; chearset=utf-8'}

cap = cv2.VideoCapture(1)

if not cap.isOpened():
  exit()

while True:
    ret, img_bgr = cap.read()
    img_str = base64.b64encode(cv2.imencode('.jpg', img_bgr)[1]).decode()
    img_dict = {'img':img_str}
    img_dict = json.dumps(img_dict)
    response = requests.post('http://127.0.0.1:8080/', data=img_dict, headers=headers)

    data = response.json()
    data = base64.b64decode(data['img'])
    jpg_arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(jpg_arr, cv2.IMREAD_COLOR)
    cv2.imshow('img', img)
    
    if cv2.waitKey(500) == ord('q'):
        break

cap.release()
