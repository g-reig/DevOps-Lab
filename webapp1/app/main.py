from flask import Flask
import socket
import os
from flask import request

app = Flask(__name__)

@app.route("/bye")
def bye_world():
    os.system(f'ls {request.args.get("folder")}')
    return "Bye! I am {} by the way.".format(socket.gethostname())
