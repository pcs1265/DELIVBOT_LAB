#전역 공유 변수를 정의

import pymysql
import roslibpy
import roslibpy.actionlib

#position
#   x
#   y
#orientation
#   w
#   w
def recv_pos(received_data):
    global currrent_pose
    currrent_pose = received_data['pose']['pose']
    return

#status
#text
def recv_status(received_data):
    global currrent_status
    status_list = received_data['status_list']
    if(len(status_list) == 0):
        #move_base 노드가 시작되고 아무 Action이 주어지지 않았을 때의 예외 발생 방지
        currrent_status = {'status': 0, 'text':"There's no action status"}
    else:
        currrent_status = status_list[len(status_list)-1]
    return


def initialize():
    #ROS와 연결 수립
    global client
    client = roslibpy.Ros(host='10.8.0.1', port=9090)
    client.run()

    #로봇에 명령을 내릴 액션 클라이언트 정의
    global action_client
    action_client = roslibpy.actionlib.ActionClient(client, '/move_base', 'move_base_msgs/MoveBaseAction')
    
    #로봇에게 내려진 마지막 명령
    global last_goal
    last_goal = None

    #로봇 상태를 가져오는 리스너 정의
    #pos: 로봇의 위치, 방향
    #status: 액션 목표의 상태
    pos_listener = roslibpy.Topic(client, '/amcl_pose', 'geometry_msgs/PoseWithCovarianceStamped')
    status_listener = roslibpy.Topic(client, '/move_base/status', 'actionlib_msgs/GoalStatusArray')
    
    #각 로봇 상태 구독
    global currrent_pose
    global currrent_status
    pos_listener.subscribe(recv_pos)
    status_listener.subscribe(recv_status)

    #cmd_vel 토픽을 발행하는 객체 정의
    global cmd_topic
    cmd_topic = roslibpy.Topic(client, '/cmd_vel', 'geometry_msgs/Twist', throttle_rate=50)
    cmd_topic.advertise()

    #DB 연결 수립
    global database
    database = pymysql.connect(host='localhost', user='pcs1265', password='#cs000218',db='robotLAB', charset='utf8')

    global cmd_center
    cmd_center = {
        #커맨드 센터 상태변수
        #0 : 명령 대기중
        #1 : 목적지로 이동중
        #2 : 로봇의 작업 완료 대기중(도착후 3분 or 사용자 작업 완료 대기중)
        #3 : 복귀중
        'status': (0, "Waiting for request"),
        'target_document': None,
    }

#ROS 연결 종료
def terminate():
    database.close()
    client.terminate()