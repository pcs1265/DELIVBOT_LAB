# DELIVBOT_LAB

팀원으로 함께 해주신 분들 감사합니다.

<img src="https://github.com/pcs1265/DELIVBOT_LAB/assets/67962828/b97ce50a-0cb6-4b7b-9f8f-ef322545b270" alt="drawing" width="500"/>

## 특징
1. 수령자 얼굴 인증 (불가시 인증 위한 일회용 QR 코드 발급)
2. 웹 사용자 인터페이스 (배달 요청, 실시간 로봇 위치 등)
3. 솔레노이드 잠금장치
4. LiDAR 활용 자율 주행 (ROS)

## 사용기술
로봇 관제 서버 :
- Python Flask with roslibpy
    
데이터베이스 :
- MySQL
    
얼굴인식 시스템 :
- Face Recognition library
- Intel Depth Camera for validate real face
- Python Flask for communication

로봇 :
- GUI - PyQt 5
- 잠금장치 = Serial Comm between Arduino and Jetson Nano 
