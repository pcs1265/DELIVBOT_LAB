from flask import Blueprint
import rosclient

statusAPI = Blueprint("status", __name__, template_folder="templates")

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
@statusAPI.route('/robot', methods=["GET"])
def robot_status():
    currrent_pose = rosclient.currrent_pose
    currrent_status = rosclient.currrent_status
    response = {
        "pos_x" : currrent_pose['position']['x'],
        "pos_y" : currrent_pose['position']['y'],
        "ori_w" : currrent_pose['orientation']['w'],
        "ori_z" : currrent_pose['orientation']['z'],
        "status_code" : currrent_status['status'],
        "status_text" : currrent_status['text']
    }
    return response

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
@statusAPI.route('/cmd', methods=["GET"])
def cmd_status():
    currrent_pose = rosclient.currrent_pose
    currrent_status = rosclient.currrent_status
    response = {
        "pos_x" : currrent_pose['position']['x'],
        "pos_y" : currrent_pose['position']['y'],
        "ori_w" : currrent_pose['orientation']['w'],
        "ori_z" : currrent_pose['orientation']['z'],
        "status_code" : currrent_status['status'],
        "status_text" : currrent_status['text']
    }
    return response
