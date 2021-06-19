import time

import pigpio
import os
from time import sleep

RX = 19
TX = 26

pi = pigpio.pi()

if not pi.connected:
    # if the daemon is not running, start it
    print("Not connected trying again...")
    os.system("sudo pigpiod")
    sleep(1)
    pi = pigpio.pi()
    

pi.set_mode(RX, pigpio.INPUT)
pi.set_mode(TX, pigpio.OUTPUT)

def Sendline(serialpi, command):
    
    command = command.upper()
    command_str = f"{command}\r\n".encode()
    serialpi.wave_clear()
    serialpi.wave_add_serial(TX, 9600, command_str)
    wid=serialpi.wave_create()
    serialpi.wave_send_once(wid)
    while serialpi.wave_tx_busy():
        pass
    serialpi.wave_delete(wid)


def Readline(timeout=1):
    
    pigpio.exceptions = False
    pi.bb_serial_read_close(RX)
    # fatal exceptions back on
    pigpio.exceptions = True
    pi.bb_serial_read_open(RX, 9600)  # open the port, 8 bits is default

    endl = b'\n'
    data_string = ''
    data_list = ''

    start_time = time.time_ns()
    while True:

        (b_count, data) = pi.bb_serial_read(RX)
        # print(data, f" :: {pi.wave_tx_busy()}")
        # print(f"{time.time_ns() - start_time} and {((1/9600)*1e9)*10}")
        if data:
            # print(data, (f" Time :: {time.time_ns() - start_time} ns"))

            ## Try decoding the data
            try:
                data_s = data.decode("utf-8", "ignore")
                data_list += data_s
                print(data_s, end="")

            except Exception as e:
                print(f"Could not decode string: {e}")
                break
            # print("outide!")
            start_time = time.time_ns()

        if (time.time_ns() - start_time) >= ((timeout)*1e9):
            print("breaking..", (f" Time :: {time.time_ns() - start_time} ns"))
            print(f"DATA LIST:: {data_list}")
            break




# Sendline(pi, "AT+CSPN?")
# Sendline(pi, "AT+CMGF=1")
# Readline()
# Sendline(pi, "AT+CNMI=2,2,0,0,0")
# Readline(50)

Sendline(pi, "AT+CMGF=1")
Readline()
Sendline(pi, "AT+CMGS=\"+254722534687\"")
Readline()
Sendline(pi, "Message Test Responce")
Readline()
Sendline(pi, "\x1A")
Readline()

print("Wolan!")
