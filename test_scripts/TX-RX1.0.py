import pigpio

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

def Sendline(serialpi):
    serialpi.wave_clear()
    serialpi.wave_add_serial(TX, 9600, b'AT+CSQ\r\n')
    wid=serialpi.wave_create()
    serialpi.wave_send_once(wid)
    while serialpi.wave_tx_busy():
        pass
    serialpi.wave_delete(wid)

Sendline(pi)

pigpio.exceptions = False
pi.bb_serial_read_close(RX)
# fatal exceptions back on
pigpio.exceptions = True
pi.bb_serial_read_open(RX, 9600)  # open the port, 8 bits is default



while True:
    (b_count, data) = pi.bb_serial_read(RX)
    if data:
        print(data, b_count)