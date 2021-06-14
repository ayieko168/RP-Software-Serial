import pigpio
import time
import sys
import traceback
import os

baudrate = 9600
DEBUG = True

txPin = 19#20
rxPin = 26#21


serialpi=pigpio.pi()
serialpi.set_mode(rxPin, pigpio.INPUT)
serialpi.set_mode(txPin, pigpio.OUTPUT)

pigpio.exceptions = False
serialpi.bb_serial_read_close(rxPin)
pigpio.exceptions = True

serialpi.bb_serial_read_open(rxPin, baudrate, 8)

def Sendline(serialpi):
    serialpi.wave_clear()
    serialpi.wave_add_serial(txPin, baudrate, b'AT\r\n')
    wid=serialpi.wave_create()
    serialpi.wave_send_once(wid)
    while serialpi.wave_tx_busy():
        pass
    serialpi.wave_delete(wid)
    
    dataa = serialpi.bb_serial_read_close(rxPin)
    print(dataa)

def SendSMS(serialpi):
    serialpi.wave_clear()
    serialpi.wave_add_serial(txPin,baudrate,b'AT+CMGS=\"+254722534687\"\r\n')
    wid=serialpi.wave_create()
    serialpi.wave_send_once(wid)
    while serialpi.wave_tx_busy():
        pass
    serialpi.wave_delete(wid)
    
def SendMessage(serialpi):
    serialpi.wave_clear()
    serialpi.wave_add_serial(txPin,baudrate,b'TEST\r\n')
    wid=serialpi.wave_create()
    serialpi.wave_send_once(wid)
    while serialpi.wave_tx_busy():
        pass
    serialpi.wave_delete(wid) 

def EndMessage(serialpi):
    serialpi.wave_clear()
    serialpi.wave_add_serial(txPin, baudrate, '26')
    wid=serialpi.wave_create()
    serialpi.wave_send_once(wid)
    while serialpi.wave_tx_busy():
        pass
    serialpi.wave_delete(wid) 

Sendline(serialpi)

bol = "G"   # beginning of line starts with "Gate"
eol = "\r"  # end of line is "\r\n"

# instantiate an empty dict to hold the json data
display_data = {}
str_s = ""  # holds the string building of segments
str_r = ""  # holds the left-over from a previous string which may contain
                # the start of a new sentence

if DEBUG : print("start processing...")
try:
    while True:
        # get some data. The bb_serial_read will read small segments of the string
        # so they need to be added together to form a complete sentence.
        (b_count, data) = serialpi.bb_serial_read(rxPin)  # b_count is byte count of data
        #if int(b_count) > 0: print("b_count: {} data: {}".format(int(b_count), data))
        # wait for the start of a new sentence, it starts with a begin-of-line(bol)
        if (int(b_count) == 0): # wait for real data
            continue
        # we have data
        # decode to ascii first so we can use string functions
        try:
            data_s = data #.decode("utf-8", "ignore") # discard non-ascii data
            if DEBUG: print(data_s)
        except AttributeError as e:
            print('*** Decode error: {}'.format(e))
            continue
        # add the left-over from the previous string if there was one
        data_s = str_r + data_s
        if DEBUG: print(data_s)
        #  look for the bol in this segment
        if bol in data_s:
            if DEBUG: print("found bol")
            pos = data_s.find(bol)  # get the position of the bol
            # save the start of the sentence starting with bol
            str_s = right(data_s, pos)  # strip everything to the left
            # look to see if there are more bol's in this segment
            if str_s.count(bol) > 1 :   # there is another one!
                # skip the first and get the position of the second bol
                pos = str_s[1:].find(bol)
                if DEBUG : print(pos)
                # strip everything to the left of the second bol
                str_s = right(str_s, pos+1)
            if DEBUG: print(str_s)

            # get more data segments to complete the sentence
            while (int(b_count) > 0):
                #if DEBUG : print("building string")
                (b_count, data) = serialpi.bb_serial_read(rxPin)
                #if DEBUG : print("b_count: {} data: {}".format(int(b_count), data))
                if int(b_count) == 0 : # only process real data
                    b_count = 1  # stay in this while loop
                    continue
                # decode to ascii
                try:
                    data_s = data #.decode("utf-8", "ignore")
                except ValueError.ParseError as e:
                    print('*** Decode error: {}'.format(e))
                    continue

                # look for the eol "\r" of the sentence
                if eol in data_s:
                    if DEBUG: print("found eol")
                    pos = data_s.find(eol)
                    if DEBUG: print("eol position ",pos)
                    str_r = left(data_s, pos)  # use everything to the left of the eol
                    str_s = str_s +  str_r     # finish the sentence
                    if DEBUG : print("received string = {}".format(str_s))
                    # create a starting timestamp so we can calculate the time
                    # left before we get the next sample
                    tstamp_s = int(time.time()/60)+1  # 16.6 or 166.6 minutes
                    # process the results and write them to a file
                    process_data(str_s, tstamp_s)
                    # save the left-over, which can be the start of a new sentence
                    str_r = right(data_s, pos+1)
                    # if we have a single "\n", discard it
                    if str_r == "\n" :
                        str_r = ""   # skip the \n part of the eol

                    if DEBUG: print("left over", str_r)
                    # start looking for a bol again
                    break
                else:
                    # add the segments together
                    str_s = str_s +  data_s
                    if DEBUG: print(str_s)
                    # get more segments to complete the sentence

        else:
            # continue looking for the start of a segment
            str_s = ""
            data_s = ""
            continue


except KeyboardInterrupt: # Ctrl-C
    print("\nCtrl-C - Terminated")
    os._exit(1)

except Exception as e:
    sys.stderr.write("Got exception: {}".format(e))
    print(traceback.format_exc())
    os._exit(1)

print('sent')
time.sleep(.5)