from rpiSS import SoftwareSerial

from flask import Flask
from flask import request

import random
import threading

app = Flask(__name__)

## Set the modules in listen mode
ser0 = SoftwareSerial(baudrate=9600, txPin=26, rxPin=19)
ser0.write("AT+CMGF=1")
dat = ser0.readString(verbose=True, timeout=0.5); print(dat)
ser0.write("AT+CNMI=2,2,0,0,0")
dat = ser0.readString(verbose=True, timeout=0.5); print(dat)

def readIncomingSMS():
    
    ser0 = SoftwareSerial(baudrate=9600, txPin=26, rxPin=19)
    ret_val = ser0.readString(timeout=120, verbose=True)

# Start the listening thread
th0 = threading.Thread(target=readIncomingSMS)
th0.start()

@app.route('/send', methods=['POST'])
def index():

    content = request.get_json()
    print(content)
    
    try:
        phone_to = content['phone_to']
        message = content['message']
        
        sendSMS(str(phone_to), str(message))
        
    except Exception as e:
        print("Wrong data recieved!")
        return "False"
    
    
    return "True"
    
def sendSMS(number, message):
    
    ser0 = SoftwareSerial(baudrate=9600, txPin=26, rxPin=19)
    ser1 = SoftwareSerial(baudrate=9600, txPin=20, rxPin=21)
    ser2 = SoftwareSerial(baudrate=9600, txPin=16, rxPin=12)
    ser3 = SoftwareSerial(baudrate=9600, txPin=24, rxPin=23)
    
    serial_ports = [ser0, ser1, ser2, ser3]
    ser = random.choice(serial_ports)
    
    print(f"Used Serial :: {ser}")
    
    ret = ser.test_connection()
    
    ser.write("AT+CMGF=1")
    dat = ser.readString(verbose=True, timeout=0.5); print(dat)

    ser.write(f"AT+CMGS=\"{number}\"")
    dat = ser.readString(verbose=True, timeout=0.5); print(dat)

    ser.write(message)
    dat = ser.readString(verbose=True, timeout=0.5); print(dat)
    
    ser.write("\x1A")
    dat = ser.readString(verbose=True, timeout=0.5); print(dat)



 
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2323)
    print("running")



