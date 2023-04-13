import roslibpy
from flask import Blueprint, request
import rosclient

cmd_velAPI = Blueprint("cmd_vel", __name__, template_folder="templates")


#요청형식
#URL: http://hostname:5000/cmd_vel/
#Content-Type : application/json
#{
#   'linear_velocity': 실수
#   'angular_velocity': 실수
#}

#유의미한 응답을 반환하지 않음(즉 HTTP응답 200 = 성공)
@cmd_velAPI.route('/', methods=["POST"])
def cmd_vel():
    data = request.json
    vel_msg = roslibpy.Message(
        {
            'linear': {
                        "z":0,
                        "y":0,
                        "x":data['linear_velocity']
            }
            ,
            'angular': {
                        'z':data['angular_velocity'],
                        'y':0,
                        'x':0
            }
        }
    )
    rosclient.cmd_topic.publish(vel_msg)
    return ""