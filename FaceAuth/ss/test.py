import numpy as np
import dlib
import cv2
import time

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects

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
        face_descriptor = facerec.compute_face_descriptor(img, shape)
        face_descriptors.append(np.array(face_descriptor))
    
    return np.array(face_descriptors)

def draw_text(img, text, x, y):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_thickness = 2
    text_color=(255, 255, 255)
    text_color_bg=(0, 0, 0)

    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    offset = 5

    cv2.rectangle(img, (x - offset, y - offset), (x + text_w + offset, y + text_h + offset), text_color_bg, -1)
    cv2.putText(img, text, (x, y + text_h + font_scale - 1), font, font_scale, text_color, font_thickness)

img_paths = {
    'pcs': 'img/pcs.jpg',
    'duboo': 'img/duboo.png'
}

descs = {
    'pcs' : None,
    'duboo' : None
}

for name, img_path in img_paths.items():
    img_bgr = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    _, img_shapes, _ = find_faces(img_rgb)
    descs[name] = encode_faces(img_rgb, img_shapes)[0]

np.save('img/descs.npy', descs)
print(descs)


cap = cv2.VideoCapture(1)

if not cap.isOpened():
  exit()

# 웹캠에서 fps 값 획득
fps = cap.get(cv2.CAP_PROP_FPS)
print('fps', fps)

if fps == 0.0:
    fps = 30.0

time_per_frame_video = 1/fps
last_time = time.perf_counter()

while True:
    time_per_frame = time.perf_counter() - last_time
    time_sleep_frame = max(0, time_per_frame_video - time_per_frame)
    time.sleep(time_sleep_frame)

    real_fps = 1/(time.perf_counter()-last_time)
    last_time = time.perf_counter()
    x = 0
    y = 0
    text = '%.2f fps' % real_fps

    ret, img_bgr = cap.read()
    if not ret:
        break

    img_bgr = cv2.resize(img_bgr, (320, 180))

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    rects, shapes, _ = find_faces(img_rgb)

    

    descriptors = encode_faces(img_rgb, shapes)

    for i, desc in enumerate(descriptors):
        last_found = {'name': 'unknown', 'dist': 0.6, 'color': (0,0,255)}

        for name, saved_desc in descs.items():
            dist = np.linalg.norm([desc] - saved_desc, axis=1)
            
            if dist < last_found['dist']:
                last_found = {'name': name, 'dist': dist, 'color': (255,255,255)}

        cv2.rectangle(img_bgr, pt1=rects[i][0], pt2=rects[i][1], color=last_found['color'], thickness=2)
        cv2.putText(img_bgr, last_found['name'], org=rects[i][0], fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=last_found['color'], thickness=2)

    draw_text(img_bgr, text, x, y)
    cv2.imshow('img', img_bgr)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()

