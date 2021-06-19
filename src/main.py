from rpiSS import SoftwareSerial

from flask import Flask
from flask import request

import random
import threading
from concurrent.futures import ThreadPoolExecutor
import pigpio

## global variables
read_state = True  # Check whether to keep read state on or close it
MAX_WORKERS = 10

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


def readSMSString(serial_obj):
    
    print(f"Listennig for sms on port {serial_obj}")
    
    def reader():
        
        wait_next = False
        verbose = True
        
        pigpio.exceptions = False
        serial_obj.pi.bb_serial_read_close(serial_obj.rxPin)
        # fatal exceptions back on
        pigpio.exceptions = True
        serial_obj.pi.bb_serial_read_open(serial_obj.rxPin, serial_obj.baudrate)  # open the port, 8 bits is default

        data_string = ''
        phone_number = ''
        message_date = ''
        actual_message = ''

        while True:

            (b_count, data) = serial_obj.pi.bb_serial_read(serial_obj.rxPin)

            if data:
                print(data)
                wait_next = True
                ## Try decoding the data
                try:
                    data_s = data.decode("utf-8", "ignore")
                    data_string += data_s
                    if data_s == "\n":
                        # print(f"wait_next val :: {wait_next}")
                        # print(f"Data String {data_string}")
                        if "+CMT" in data_string:
                            print(f"MESSAGE INFO: {data_string}")
                            phone_number = data_string.split("\"")[1]
                            message_date = data_string.split("\"")[5]
                            wait_next = False
                        
                        if wait_next:
                            print(f"MESSAGE: {data_string}")
                            actual_message = data_string
                            wait_next = False
                        
                        if (phone_number.strip() != '' and actual_message.strip() != ''):
                            print(f"SEND MESSAGE :: message - {actual_message}, phone_to - {phone_number}")
                            
                            
                        data_string = ''
                        phone_number = ''
                        message_date = ''
                        actual_message = ''
                        
                    # if verbose: print(data_s, end="")

                except Exception as e:
                    if verbose: print(f"Could not decode string: {e}")
                    break
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



