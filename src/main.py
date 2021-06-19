from rpiSS import SoftwareSerial

from flask import Flask
from flask import request

import random
import threading
from concurrent.futures import ThreadPoolExecutor
import pigpio
import requests

## global variables
read_state = True  # Check whether to keep read state on or close it
MAX_WORKERS = 10
URL = "https://dpkosing.azurewebsites.net/api/Messages/sms"

## Create the GSM serial objects
ser0 = SoftwareSerial(baudrate=9600, txPin=26, rxPin=19)
ser1 = SoftwareSerial(baudrate=9600, txPin=20, rxPin=21)
ser2 = SoftwareSerial(baudrate=9600, txPin=16, rxPin=12)
ser3 = SoftwareSerial(baudrate=9600, txPin=24, rxPin=23)
# List of all available serial ports
serial_ports = [ser0, ser1, ser2, ser3]


def setListen(serialsList):

    for serObj in serialsList:

        serObj.write("AT+CMGF=1")
        dat = serObj.readString(verbose=True, timeout=0.25); print(dat)
        serObj.write("AT+CNMI=2,2,0,0,0")
        dat = serObj.readString(verbose=True, timeout=0.25); print(dat)


def postSMS(from_number, message):

    print(f"Forwarding sms from {from_number}...")

    def send():

        r = requests.post(URL, json={'from': str(from_number), 'body': str(message)})
        print((from_number, r.status_code, r.reason))
    
    threading.Thread(target=send).start()



def readSMSString(serial_obj: SoftwareSerial):
    
    print(f"Listennig for sms on port {serial_obj}")
    
    def reader():
        
        while True:
            
            real_data = serial_obj.readSMS(timeout=1, verbose=False)

            if len(real_data) > 0:
                # print(f"received data from sim sms listen == {real_data}")

                ## perse for the message if the sms is valid
                if '+CMT' in real_data:
                    data_list = real_data.splitlines(keepends=False)

                    from_number = data_list[1].split('\"')[1]
                    parsed_message = ' '.join(data_list[2:])

                    print(f"\nNEW MESSAGE: From: {from_number} Message: {parsed_message}")

                    ## Send The SMS to SERVER
                    postSMS(from_number, parsed_message)

                # except Exception as e:
                #     if verbose: print(f"Could not decode string: {e}")
                #     break
                # print("outide!")

    threading.Thread(target=reader).start()



def sendSMS(number, message):

    ser = random.choice(serial_ports)

    print(f"Used Serial :: {serial_ports.index(ser)}")

    ret = ser.test_connection()

    ser.write("AT+CMGF=1")
    dat = ser.readString(verbose=True, timeout=0.5); print(dat)

    ser.write(f"AT+CMGS=\"{number}\"")
    dat = ser.readString(verbose=True, timeout=0.5); print(dat)

    ser.write(message)
    dat = ser.readString(verbose=True, timeout=0.5); print(dat)

    ser.write("\x1A")
    dat = ser.readString(verbose=True, timeout=0.5); print(dat)


## Configure the listening server
app = Flask(__name__)

## Set the serial devices to listening mode
print(f"Setting the serial devices to listening mode")
setListen(serial_ports)

#Start the listening thread
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    executor.map(readSMSString, serial_ports)


@app.route('/send', methods=['POST'])
def index():

    content = request.get_json()
    print(f"DATA RECIVED : {content}, type: {type(content)}")
    
    try:
        phone_to = content['To']
        message = content['Body']
        
        sendSMS(str(phone_to), str(message))
        
    except Exception as e:
        print("Wrong data recieved!")
        return "False"
    
    
    return "True"



if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=2323)
    print("running")



