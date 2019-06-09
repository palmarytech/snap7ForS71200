import snap7.client as client
import snap7
from snap7.util import *


def write_output(dev, byte, bit, cmd):
    data = dev.read_area(0x82, 0, byte, 1)
    set_bool(data, byte, bit, cmd)
    dev.write_area(0x82, 0, byte, data)


s71200 = snap7.client.Client()
s71200.connect('192.168.100.2', 0, 1)
connectionIsOk = s71200.get_connected()
print(connectionIsOk)

write_output(s71200, 0, 0, True)

