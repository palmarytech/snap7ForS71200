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


plc = snap7.client.Client()
connect(plc, '10.10.55.109', 0, 1)
while True:

    try:

        pass

    except Snap7Exception as e:

        connect(plc, '10.10.55.109', 0, 1)
        # break
