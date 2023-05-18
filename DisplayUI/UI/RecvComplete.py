from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from threading import Thread

import shared
import requests
import json

class RecvComplete(QMainWindow):
    def __init__(self, id, name):
        super().__init__()
        loadUi("UI/RecvComplete.ui", self)
        
        self.id = id
        self.name = name

        headers = {'Content-Type': 'application/json; chearset=utf-8'}
        json_dict = {'id':self.id}
        json_data = json.dumps(json_dict)
        response = requests.get('http://127.0.0.1:5000/op/storedDocs', data=json_data, headers=headers)
        requests.post('http://127.0.0.1:5000/op/recvComplete', data=json_data, headers=headers)
        self.result = response.json()
        if(self.result['exist']):
            self.docs = self.result['docs']
            self.box_list_str = ""
            for i in  range(0, len(self.docs)):
                self.box_list_str += str(self.docs[i]['docbox_num'])
                if(i != (len(self.docs) - 1)):
                    self.box_list_str += ', '
            self.sendOpenSignal()

        self.initUI()

    def initUI(self):
        self.back_button.clicked.connect(self.close)

        if(self.result['exist']):
            self.doc_num.setText(self.name + "님의 서류는 " + str(len(self.docs)) + "개 있습니다.")
            self.box_num.setText(self.box_list_str + "번 물품함을 확인해주세요.")
        else:
            self.doc_num.setText(self.name + "님을 대상으로 하는 서류가 없습니다.")
            self.box_num.setText("메인화면으로 이동하려면 아래 버튼을 눌러주세요.")
            self.back_button.setText("메인화면")
        
        return

    def sendOpenSignal(self):

        for doc in self.docs:
            command = str(doc['docbox_num']).encode()
            shared.boxController.write(command)
        

    
    def close(self):
        shared.noInput.startTimer()
        shared.stack.removeWidget(self)

# class ScanFaceThread(QThread):

#     def __init__(self, parent, comment): 
#     	# main에서 받은 self인자를 parent로 생성
#         super().__init__(parent)        
#         self.parent = parent     
#         self.comment = comment

#     def run(self):
#         self.working = True
        

#     def stop(self):
#         self.working = False
#         self.quit()
