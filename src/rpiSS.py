import pigpio
import time

class SoftwareSerial:

    def __init__(self, baudrate, txPin, rxPin):
        """
        This
        :param baudrate: The baud rate of the serial communication device
        :param txPin: GPIO pin connected to the
        :param rxPin:
        """
        self.baudrate = baudrate
        self.txPin = txPin
        self.rxPin = rxPin
        self.pi = pigpio.pi()

        self.pi.set_mode(self.rxPin, pigpio.INPUT)
        self.pi.set_mode(self.txPin, pigpio.OUTPUT)

    def write(self, command):

        ## Create the command string - Mainly for the SIM800L and similar GSM modules
        ## Can be commented out to send raw data without courage return and end-line character
        command_str = f"{command}\r\n".encode()

        ## Create a new wave to carry oue data
        self.pi.wave_clear()
        self.pi.wave_add_serial(self.txPin, self.baudrate, command_str)
        wid = self.pi.wave_create()

        ## Send the wave to the GPIO pin, wait till sending is done
        self.pi.wave_send_once(wid)
        while self.pi.wave_tx_busy():
            pass

        ## Clear the wave for next data
        self.pi.wave_delete(wid)

    def read(self):

        pigpio.exceptions = False
        self.pi.bb_serial_read_close(self.rxPin)
        # fatal exceptions back on
        pigpio.exceptions = True

        ## open the port, 8 bits is default
        self.pi.bb_serial_read_open(self.rxPin, self.baudrate)

        ## actual reading operation
        (b_count, data) = self.pi.bb_serial_read(self.rxPin)

        return_data = (b_count, data)

        return return_data

    def readString(self, timeout=2, verbose=True):

        pigpio.exceptions = False
        self.pi.bb_serial_read_close(self.rxPin)
        # fatal exceptions back on
        pigpio.exceptions = True
        self.pi.bb_serial_read_open(self.rxPin, self.baudrate)  # open the port, 8 bits is default

        data_string = ''

        start_time = time.time_ns()
        while True:

            (b_count, data) = self.pi.bb_serial_read(self.rxPin)

            if data:

                ## Try decoding the data
                try:
                    data_s = data.decode("utf-8", "ignore")
                    data_string += data_s
                    if verbose: print(data_s, end="")

                except Exception as e:
                    if verbose: print(f"Could not decode string: {e}")
                    break
                # print("outide!")
                start_time = time.time_ns()

            if (time.time_ns() - start_time) >= (timeout*1e9):
                if verbose: print(f"Breaking.., Time :: {time.time_ns() - start_time} ns, DATA LIST:: {data_string}")
                break

        return data_string

    def test_connection(self, timeout=0.5, verbose=True):

        self.write("AT")
        ret_val = self.readString(timeout=timeout, verbose=verbose)

        if "OK".upper() in ret_val:
            return True
        else:
            if verbose: print(f"Return Data :: {ret_val}")
            return False


if __name__ == '__main__':

    ser = SoftwareSerial(baudrate=9600, txPin=26, rxPin=19)
    #ser = SoftwareSerial(baudrate=9600, txPin=20, rxPin=21)
    #ser = SoftwareSerial(baudrate=9600, txPin=16, rxPin=12)
    #ser = SoftwareSerial(baudrate=9600, txPin=24, rxPin=23)
    
    ret = ser.test_connection()
    ser.write("AT+CCFC=?")
    dat = ser.readString(verbose=False, timeout=1); print(dat)

    # ser.write("AT+CMGS=\"+254723410282\"")
    # dat = ser.readString(verbose=False, timeout=1); print(dat)

    # ser.write("TEst v4")
    # dat = ser.readString(verbose=True, timeout=1); print(dat)
    
    # ser.write("\x1A")
    # dat = ser.readString(verbose=True, timeout=5); print(dat)
    # # print(dat)



