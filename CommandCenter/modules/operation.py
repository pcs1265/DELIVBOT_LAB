import pymysql
import json
import time
from datetime import datetime
from threading import Thread

import roslibpy
from flask import Blueprint, request
import rosclient, utils

operationAPI = Blueprint("operation", __name__, template_folder="templates")

 #커맨드 센터 상태변수
#명령 대기중
status_waiting_for_request = (0, "Waiting for request")
#1 : 목적지로 이동중
status_navigating = (1, "Navigating to given goal")
#2 : 사용자의 서류 수령, 발송 완료 대기중(무한정대기?)
status_waiting_for_robot_complete = (2, "Waiting for user action to complete")
#3 : 복귀중
status_returning_to_default_position = (3, "Returning to default position")

robot_cmd_publisher = roslibpy.Topic(rosclient.client, '/robot_cmd', 'std_msgs/String')
robot_cmd_publisher.advertise()

robot_cmd = (False, 0)

def waitForCompleteAction(goal):
    
    goal.wait()
    print(goal.status)
    if(goal.status['status'] == 3):
        rosclient.cmd_center['status'] = status_waiting_for_robot_complete
        global robot_cmd
        robot_cmd = (True, 0)
    else:
        rosclient.cmd_center['status'] = status_waiting_for_request

#cmd_code Rules
#0 : 목적지 도착
#1 : 출발 대기 시작


def getCandFromDB():
    # 데이터베이스 커서 생성
    cur = rosclient.database.cursor()
    
    # SQL Delivery 규칙
    # 0 : 배달대기
    # 1 : 배달중
    # 2 : 유기
    # 3 : 배달완료
    sql = "SELECT d.user_id, u.room_num, u.building_num, d.doc_id, r.room_loc " \
          "FROM doc_table d " \
          "JOIN user_table u ON d.user_id = u.user_id " \
          "JOIN room_table r ON u.room_num = r.room_name AND u.building_num = r.building_name " \
          "WHERE d.status = 0 AND r.room_in = 1"
    
    # SQL문 실행
    cur.execute(sql)
    
    # 실행된 결과 가져오기
    rows = cur.fetchall()
    
    # 데이터베이스 커밋
    rosclient.database.commit()

    return rows

def getDestFromDB():
    rows = getCandFromDB()

    # 후보 목록 초기화
    candidates = []
    
    # 후보 목록 생성
    for candidate in rows:
        cand_unit = {
            "user_id" : candidate[0],
            "room_num" : candidate[1],
            "building_num" : candidate[2],
            "doc_id" : candidate[3],
            "room_loc" : json.loads(candidate[4])
        }
        candidates.append(cand_unit)
    
    # 현재 로봇 위치
    current_position = rosclient.currrent_pose['position']

    # 가장 가까운 목적지 찾기
    min_cand = None
    min_dist = 987654321
    for cand in candidates:
        room_loc = cand['room_loc']
        diff_x = room_loc['x'] - current_position['x']
        diff_y = room_loc['y'] - current_position['y']
        dist = diff_x * diff_x + diff_y * diff_y
        if(dist < min_dist):
            min_dist = dist
            min_cand = cand
    
    # 가장 가까운 목적지 반환
    return min_cand

def makeGoalFromDB():

    dest = getDestFromDB()
    
    if(dest == None):
        print('대상 없음!!')
        return
    else:
        #전송할 목표 메시지 정의
        print(dest)

        if rosclient.cmd_center['status'] != status_waiting_for_request:
            return 

        dest_coord = dest['room_loc']
        goal = utils.getGoalObject(dest_coord['x'], dest_coord['y'], dest_coord['w'], dest_coord['z'])

        #마지막 전송 목표 저장
        rosclient.last_goal = goal
        th1 = Thread(target=waitForCompleteAction, args=(goal,))

        th1.start()
 
        rosclient.cmd_center['status'] = status_navigating
        rosclient.cmd_center['target_document'] = dest['doc_id']
        #목표 전송
        goal.send()    
    

#요청형식
#URL: http://hostname:5000/op/checkDB
#data 무관

#유의미한 반환 내용 없음
@operationAPI.route('/checkDB', methods=["POST"])
def checkDB():
    if(rosclient.cmd_center['status'][0] == status_waiting_for_request[0]):
        makeGoalFromDB()
    return ""


@operationAPI.route('/userOccupation', methods=["POST"])
def robotUsing():
    rosclient.cmd_center['status'] = status_waiting_for_robot_complete
    return ""

@operationAPI.route('/userOccupation', methods=["DELETE"])
def robotDone():

    if(rosclient.cmd_center['status'][0] == status_waiting_for_robot_complete[0]):
        rosclient.cmd_center['status'] = status_waiting_for_request
        print("사용자 작업 완료")
        makeGoalFromDB()
    return ""

@operationAPI.route('/pending', methods=["GET"])
def isPending():
    if(len(getCandFromDB()) > 0):
        return {"isPending" : True}
    else:
        return {"isPending" : False}

@operationAPI.route('/pollstate', methods=["GET"])
def pollState():
    timeout = 10  # 10초의 타임아웃 설정
    start_time = time.time()  # 현재 시간 기록
    global robot_cmd
    
    while True:
        # 새로운 이벤트가 발생하면 이벤트를 반환
        if robot_cmd[0]:
            response = {
                "cmd_code" : robot_cmd[1]
            }
            robot_cmd = (False, 0)
            return response

        # 타임아웃이 발생하면 빈 응답을 반환
        if time.time() - start_time > timeout:
            return ("", 204)

        # 일정 시간 동안 대기한 후 다시 반복
        time.sleep(1)