import serial

import time

py_serial = serial.Serial(
    
    # Window
    port='/dev/ttyACM0',
    
    # 보드 레이트 (통신 속도)
    baudrate=9600,
)

time.sleep(3)

while True:
    

    command = 's'
    time.sleep(1)

    py_serial.write(command.encode())

    if py_serial.readable():
        
        # 들어온 값이 있으면 값을 한 줄 읽음 (BYTE 단위로 받은 상태)
        # BYTE 단위로 받은 response 모습 : b'\xec\x97\x86\xec\x9d\x8c\r\n'
        response = py_serial.readline()
        
        # 디코딩 후, 출력 (가장 끝의 \n을 없애주기위해 슬라이싱 사용)
        print(response[:len(response)-1].decode())