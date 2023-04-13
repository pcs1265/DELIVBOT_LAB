import roslibpy
from flask import Blueprint, request
import rosclient, utils

actionAPI = Blueprint("action", __name__, template_folder="templates")


#요청형식
#URL: http://hostname:5000/action/
#Content-Type : application/json
#{
#   'pos_x': 실수
#   'pos_y': 실수
#   'ori_w': 실수
#   'ori_z': 실수
#}

#Action이 종료되면 응답을 반환

#반환형식 : JSON
#{
#   'result': 정수
#   'elapsed_time': 정수
#}
@actionAPI.route('/', methods=["POST"])
def make_action():
    #요청의 데이터는 JSON
    data = request.json

    #전송할 목표 메시지 정의
    
    goal = utils.getGoalObject(data['pos_x'], data['pos_y'], data['ori_w'], data['ori_z'])

    #마지막 전송 목표 저장
    rosclient.last_goal = goal

    #목표 전송
    goal.send()

    #소요 시간을 위한 현재 시간 저장
    send_time = roslibpy.Time.now()

    #목표 완료까지 대기후 응답 전송
    #사용자 요청으로 목표가 취소되거나 새로운 액션요청으로 인해 취소되더라도 응답을 전송함
    goal.wait()
    
    response = {
        "result" : goal.status['status'],
        "elapsed_time" : roslibpy.Time.now()['secs'] - send_time['secs']
    }
    return response


#요청형식
#URL: http://hostname:5000/action/
@actionAPI.route('/', methods=["DELETE"])
def cancel():
    rosclient.last_goal.cancel()
    return ""