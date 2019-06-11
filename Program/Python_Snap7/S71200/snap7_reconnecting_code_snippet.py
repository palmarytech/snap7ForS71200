from time import sleep
import snap7.client as client
import snap7
from snap7.snap7exceptions import Snap7Exception
from snap7.util import *

def connect(device, ip, rack, slot):
    while True:
        # check connection
        if device.get_connected():
            break
        try:
            # attempt connection
            device.connect(ip, rack, slot)
        except:
            pass
        sleep(5)

def ReadOutput(dev):
    data = dev.read_area(0x82,0,0,1)
    binary_list = [int(x) for x in bin(data[0])[2:]]
    print(binary_list)

def main():
    s71200 = snap7.client.Client()
    connect(s71200, '192.168.2.110', 0, 1)
    while True:
        try:
            ReadOutput(s71200)
            sleep(5)
        except Snap7Exception as e:
            connect(s71200, '192.168.2.110', 0, 1)

if __name__ == '__main__':
    main()
