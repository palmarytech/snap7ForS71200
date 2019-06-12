from time import sleep
import snap7
from snap7.snap7exceptions import Snap7Exception
from snap7.util import *
from snap7.snap7types import *

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


def ReadMemory(dev,byte,bit,datatype):
    result = dev.read_area(0x83,0,byte,datatype)
    if datatype==S7WLBit:
        return get_bool(result,0,bit)
    elif datatype==S7WLByte or datatype==S7WLWord:
        return get_int(result,0)
    elif datatype==S7WLReal:
        return get_real(result,0)
    elif datatype==S7WLDWord:
        return get_dword(result,0)
    else:
        return None


def WriteMemory(dev,byte,bit,datatype,value):
    result = dev.read_area(0x83,0,byte,datatype)
    if datatype==S7WLBit:
        set_bool(result,0,bit,value)
    elif datatype==S7WLByte or datatype==S7WLWord:
        set_int(result,0,value)
    elif datatype==S7WLReal:
        set_real(result,0,value)
    elif datatype==S7WLDWord:
        set_dword(result,0,value)
    dev.write_area(0x83,0,byte,result)


def main():
    s71200 = snap7.client.Client()
    connect(s71200, '192.168.2.110', 0, 1)
    while True:
        try:
            print(ReadMemory(s71200, 410, 0, S7WLReal))
            sleep(1)
            WriteMemory(s71200, 420, 0, S7WLReal, 78.65)
            sleep(1)
            print(ReadMemory(s71200, 420, 0, S7WLReal))
            sleep(5)
        except Snap7Exception as e:
            connect(s71200, '192.168.2.110', 0, 1)

if __name__ == '__main__':
    main()