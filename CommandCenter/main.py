from flask import Flask,render_template, request
import rosclient

rosclient.initialize()

from modules.status import statusAPI
from modules.action import actionAPI
from modules.cmd_vel import cmd_velAPI
from modules.operation import operationAPI
from modules.qrcode import QRCodeAPI

app = Flask(__name__)

#블루프린트 로드
app.register_blueprint(statusAPI, url_prefix="/status")
app.register_blueprint(actionAPI, url_prefix="/action")
app.register_blueprint(cmd_velAPI, url_prefix="/cmd_vel")
app.register_blueprint(operationAPI, url_prefix="/op")
app.register_blueprint(QRCodeAPI, url_prefix="/qrcode")

#메인 라우트
@app.route('/', methods=["GET"])
def home():
    return render_template("./index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)

rosclient.terminate()
