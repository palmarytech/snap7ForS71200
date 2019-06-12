## 通过Python实现S7-1200输出控制<二>

*版权声明*

*无需授权随便转载*

## 写输出映像区-Q区

写输出映像区的操作与读输出映像区有些许的不同，先来看看写输出映像区函数的定义

```python
def write_area(self, area, dbnumber, start, data)
```

参数和**read_area**方法一样，**area**还是按照表格里每个寄存区的定义有不同的代码，**dbnumber**只针对DB块有效，**start**是起始地址，这里的**data**参数比较特殊，它是**bytearray**类型，需要通过一个**set_bool**函数将传入的数据事先写好，先看看set_bool函数

```python
def set_bool(_bytearray, byte_index, bool_index, value):
```

第一个参数对应的就是**write_area**中的**data**参数，后两个参数是byte，bool的索引值，针对输出映像区，**byte_index**参数始终给0就行，**value**参数可以是0，1，True，False随便一个

但是因为是dataarray类型，所以最快捷的方法是先使用read_area读取输出映像区的值，之后通过set_bool赋值，之后通过write_area传入输出映像区。

定义一个**WriteOutput**函数，代码如下

```python
def WriteOutput(dev, bytebit, value):
```

dev参数是关联的设备，可以通过

```python
s71200 = snap7.client.Client()
```

创建，**bytebit**参数我希望以PLC内部常见的形式进行赋值，比如0.0，1.0，所以需要通过**split**方法对其分割，**value**参数就对应0，1，True，False

完整的函数如下

```python
def WriteOutput(dev, bytebit, value):
    #使用split分割bytebit，例如0.0，可以分割成byte = 0， bit = 0
    byte,bit = bytebit.split('.')
    byte,bit = int(byte), int(bit)
    
    #使用read_area读取输出映像区的值
    dataArray = dev.read_area(0x82, 0, byte, 1)
	#通过set_bool对dataArray赋值
    set_bool(dataArray, 0, bit, value)
	#过write_area将dataArray传入输出映像区
    dev.write_area(0x82, 0, byte, dataArray)
```

通过这个函数，可以实现对指定的输出映像区进行写操作，接下来使用这个函数，对PLC内Q0.0-Q1.7共16个输出循环写入1和0

代码如下

```python
def main():
    s71200 = snap7.client.Client()
    connect(s71200, '192.168.2.110', 0, 1)
    while True:
        try:
            #通过双层循环生成0.0~1.7
            for byte in range(2):
                for bit in range(8):
                    byte_bit = str(byte) + '.' + str(bit)
                    #调用WriteOutput函数，写入1
                    WriteOutput(s71200, byte_bit, 1)
                    sleep(1)
            for byte in range(2):
                for bit in range(8):
                    byte_bit = str(byte) + '.' + str(bit)
                    #调用WriteOutput函数，写入0
                    WriteOutput(s71200, byte_bit, 0)
                    sleep(1)
        except Snap7Exception as e:
            connect(s71200, '192.168.2.110', 0, 1)
```

效果如下图

![](C:\Users\Dave-\OneDrive - 维恩科仪（北京）机械自动化设备有限公司\WeChatArticle\snap7ForS71200\输出映像区连续写.gif)

完整代码如下

```python
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
def WriteOutput(dev, bytebit, value):
    byte,bit = bytebit.split('.')
    byte,bit = int(byte), int(bit)
    dataArray = dev.read_area(0x82, 0, byte, 1)
    binary_list = [int(x) for x in bin(dataArray[0])[2:]]
    print(binary_list)
    set_bool(dataArray, 0, bit, value)
    binary_list = [int(x) for x in bin(dataArray[0])[2:]]
    print(binary_list)
    dev.write_area(0x82, 0, byte, dataArray)
def main():
    s71200 = snap7.client.Client()
    connect(s71200, '192.168.2.110', 0, 1)
    while True:
        try:
            #ReadOutput(s71200)
            for byte in range(2):
                for bit in range(8):
                    byte_bit = str(byte) + '.' + str(bit)
                    WriteOutput(s71200, byte_bit, 1)
                    sleep(1)
            for byte in range(2):
                for bit in range(8):
                    byte_bit = str(byte) + '.' + str(bit)
                    WriteOutput(s71200, byte_bit, 0)
                    sleep(1)
        except Snap7Exception as e:
            connect(s71200, '192.168.2.110', 0, 1)
if __name__ == '__main__':
    main()
```

