import pymysql
import json
import time
from datetime import datetime
from threading import Thread
from queue import Queue

import roslibpy
from flask import Blueprint, request
import rosclient, utils

operationAPI = Blueprint("operation", __name__, template_folder="templates")

#커맨드 센터 상태변수

#0 : 명령 대기중
STATUS_WAITING_FOR_REQUEST = (0, "Waiting for request")
#1 : 목적지로 이동중
STATUS_NAVIGATING = (1, "Navigating to given goal")
#2 : 사용자의 서류 수령, 발송 완료 대기중
STATUS_USER_OCCUPATION = (2, "Waiting for user action to complete")
#3 : 복귀중
STATUS_DEFAULT_POSITION = (3, "Robot is in default position")


#cmd_code Rules
#0 : 목적지 도착
#1 : 출발 대기 시작
#2 : 이동중

robot_cmd = Queue()
robot_default_position = True

def cmd_dest_reached():
    
    global robot_cmd
    robot_cmd.put((0, None))
    return

def cmd_wait_departure():
    
    global robot_cmd
    robot_cmd.put((1, None))
    return

def cmd_navigating():
    
    global robot_cmd
    robot_cmd.put((2, None))
    return

def cmd_open_box(num):
    
    global robot_cmd
    robot_cmd.put((3, num))
    return

def cmd_returned():
    
    global robot_cmd
    robot_cmd.put((4, None))
    return

def setNullCalled(user_id):
    cur = rosclient.database.cursor()
    sql = "UPDATE user_table SET `call_time` = NULL WHERE `user_table`.`user_id` = '" + user_id + "';" \
    
    cur.execute(sql)
    rows = cur.fetchall()
    rosclient.database.commit()

    return rows

def waitForCompleteAction(goal):
    
    goal.wait()

    if(goal.status['status'] == 3):
        rosclient.cmd_center['status'] = STATUS_WAITING_FOR_REQUEST
        cmd_dest_reached()
        setNullCalled(rosclient.cmd_center['target_user'])
    else:
        rosclient.cmd_center['status'] = STATUS_WAITING_FOR_REQUEST
        cmd_wait_departure()

    global robot_default_position
    robot_default_position = False

DOC_STATUS_WAITING_DELIVERY = 0
DOC_STATUS_COMPLETED = 3

def getCandFromDB():
    # 데이터베이스 커서 생성
    cur = rosclient.database.cursor()
    
    # SQL Delivery 규칙
    # 0 : 배달대기
    # 3 : 배달완료
    sql = "SELECT u.user_id, u.room_num, u.building_num, r.room_loc, u.call_time " \
          "FROM user_table u " \
          "JOIN room_table r ON u.room_num = r.room_name AND u.building_num = r.building_name " \
          "WHERE u.call_time IS NOT NULL ORDER BY u.call_time ASC"
    
    # SQL문 실행
    cur.execute(sql)
    
    # 실행된 결과 가져오기
    rows = cur.fetchall()
    
    # 데이터베이스 커밋
    rosclient.database.commit()

    return rows

def getDestFromDB():
    rows = getCandFromDB()
    result = None
    if len(rows) != 0:
        result = {
            "user_id" : rows[0][0],
            "room_num" : rows[0][1],
            "building_num" : rows[0][2],
            "room_loc" : json.loads(rows[0][3]),
            "call" : rows[0][4]
        }
    # 가장 이른 시간에 호출한 사용자 정보 반환
    return result

def makeGoalFromDB():

    dest = getDestFromDB()
    
    if(dest == None):
        print('대상 없음!!')
        return
    else:
        #전송할 목표 메시지 정의
        print(dest)

        if rosclient.cmd_center['status'] != STATUS_WAITING_FOR_REQUEST:
            return 

        dest_coord = dest['room_loc']
        goal = utils.getGoalObject(dest_coord['x'], dest_coord['y'], dest_coord['w'], dest_coord['z'])

        #마지막 전송 목표 저장
        rosclient.last_goal = goal
        th1 = Thread(target=waitForCompleteAction, args=(goal,))

        th1.start()

        cmd_navigating()
        rosclient.cmd_center['status'] = STATUS_NAVIGATING
        rosclient.cmd_center['target_user'] = dest['user_id']
        #목표 전송
        goal.send()    
    

#요청형식
#URL: http://hostname:5000/op/checkDB
#data 무관

#유의미한 반환 내용 없음
@operationAPI.route('/checkDB', methods=["POST"])
def checkDB():
    if(rosclient.cmd_center['status'][0] == STATUS_WAITING_FOR_REQUEST[0]):
        cmd_wait_departure()
    return ""

@operationAPI.route('/openBox', methods=["POST"])
def openBox():
    data = request.json
    cmd_open_box(data['docbox_num'])

    return ""


@operationAPI.route('/makeGoal', methods=["POST"])
def makeGoal():
    makeGoalFromDB()
    return ""

@operationAPI.route('/userOccupation', methods=["POST"])
def robotUsing():
    rosclient.cmd_center['status'] = STATUS_USER_OCCUPATION
    return ""

@operationAPI.route('/userOccupation', methods=["DELETE"])
def robotDone():
    if(rosclient.cmd_center['status'][0] == STATUS_USER_OCCUPATION[0]):
        rosclient.cmd_center['status'] = STATUS_WAITING_FOR_REQUEST
    return ""

@operationAPI.route('/pending', methods=["GET"])
def isPending():
    if(len(getCandFromDB()) > 0):
        return {"isPending" : True, "inDefaultPosition" : robot_default_position}
    else:
        return {"isPending" : False, "inDefaultPosition" : robot_default_position}

@operationAPI.route('/pollCommand', methods=["GET"])
def pollCommand():
    timeout = 60  # 60초의 타임아웃 설정
    start_time = time.time()  # 현재 시간 기록
    global robot_cmd
    
    while True:
        # 새로운 이벤트가 발생하면 이벤트를 반환
        if not robot_cmd.empty():
            command = robot_cmd.get()

            response = {
                "cmd_code" : command[0]
            }
            if command[0] == 3:
                response["box"] = command[1]

            return response

        # 타임아웃이 발생하면 빈 응답을 반환
        if time.time() - start_time > timeout:
            return ("", 204)

        # 일정 시간 동안 대기한 후 다시 반복
        time.sleep(1)



@operationAPI.route('/storedDocs', methods=["GET"])
def storedDocs():
    # 데이터베이스 커서 생성
    data = request.json
    cur = rosclient.database.cursor()
    
    # 데이터베이스로부터 현재 배송완료 되지않은 문서 행 가져오기     
    sql = "SELECT d.receive_userid, d.doc_id, d.docbox_num " \
          "FROM doc_table d " \
          "WHERE d.status = 0 AND d.receive_userid = \"" + data["id"] +"\""
    
    # SQL문 실행
    cur.execute(sql)
    
    # 실행된 결과 가져오기
    rows = cur.fetchall()
    
    # 데이터베이스 커밋
    rosclient.database.commit()

    response = {}

    docs = []
    # 후보 목록 생성
    for doc in rows:
        doc_unit = {
            "user_id" : doc[0],
            "doc_id" : doc[1],
            "docbox_num" : doc[2]
        }
        docs.append(doc_unit)

    if(len(docs) == 0):
        response['exist'] = False
    else:
        response['exist'] = True
    
    response['docs'] = docs

    return response

@operationAPI.route('/recvComplete', methods=["POST"])
def recvComplete():
    # 데이터베이스 커서 생성
    data = request.json

    cur = rosclient.database.cursor()
    
    # 데이터베이스로부터 현재 배송완료 되지않은 문서 행      
    sql = "UPDATE `doc_table` SET `status` = 3, `fin_time` = now() WHERE `status` = 0 AND `doc_table`.`receive_userid` = '" + data["id"] +"'"
    
    # SQL문 실행
    cur.execute(sql)
    
    # 데이터베이스 커밋
    rosclient.database.commit()

    response = {}

    return response

def waitForCompleteReturn(goal):
    global robot_default_position

    goal.wait()

    if(goal.status['status'] == 3):
        rosclient.cmd_center['status'] = STATUS_WAITING_FOR_REQUEST
        cmd_returned()
        robot_default_position = True
    else:
        rosclient.cmd_center['status'] = STATUS_WAITING_FOR_REQUEST
        cmd_wait_departure()
        robot_default_position = False


@operationAPI.route('/returnDefaultPosition', methods=["POST"])
def returnDefaultPosition():
    if rosclient.cmd_center['status'] != STATUS_WAITING_FOR_REQUEST:
        return ""
    
    goal = utils.getGoalObject(0.331185825190603, -0.5791383213489313, 1, 0)

    #마지막 전송 목표 저장
    rosclient.last_goal = goal
    th1 = Thread(target=waitForCompleteReturn, args=(goal,))

    th1.start()

    cmd_navigating()
    rosclient.cmd_center['status'] = STATUS_NAVIGATING
    #목표 전송
    goal.send()

    return ""