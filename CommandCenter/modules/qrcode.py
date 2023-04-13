from flask import Blueprint, send_file
import rosclient
# import qrcode
import io

QRCodeAPI = Blueprint("qrcode", __name__, template_folder="templates")

#요청형식
#URL: http://hostname:5000/status/
#data 무관, 무조건 응답

#반환형식
#{
#   "pos_x" : 실수
#   "pos_y" : 실수
#   "ori_w" : 실수
#   "ori_z" : 실수
#   "status_code" : 정수
#   "status_text" : 문자열
#}
@QRCodeAPI.route('/robot', methods=["GET"])
def robot_status():
    # img = qrcode.make('https://cse.koreatech.ac.kr/')
    # img.save('qr.png')
    return ""