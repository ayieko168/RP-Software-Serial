from ..src.rpiSS import SoftwareSerial

from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/car', methods=['POST'])
def index():

    content = request.get_json()
    print(content)
    return 'DONE'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=105)
    print("running")



