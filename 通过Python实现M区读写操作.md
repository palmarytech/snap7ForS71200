## 通过Python实现M区读写操作

*版权声明*

*无需授权随便转载*



## 读M区

使用的方法依旧是read_area

```python
def read_area(self, area, dbnumber, start, size)
```

**area**是PLC内各寄存区的代码，具体参考下表

![1560245900700](C:\Users\Dave-\AppData\Roaming\Typora\typora-user-images\1560245900700.png)

**dbnumber**只针对DB块才有效，**start**为寄存区起始地址，**size**是寄存区长度

针对的是M区，所有area参数需要使用**0x83**，size参数可以通过另外一个参数进行赋值

![1560333018785](C:\Users\Dave-\AppData\Roaming\Typora\typora-user-images\1560333018785.png)

对不同的数据类型，WordLen已经定义好了长度，可以直接作为size参数使用

因为read_area方法返回的是byteArray类型的结果，可以通过get_bool，get_int，get_read，get_dword方法直接将byteArray类型转换成对应的数据类型

定义一个**ReadMemory**的函数，代码如下

```python
def ReadMemory(dev,byte,bit,datatype):
    result = dev.read_area(0x83,0,byte,datatype)
    #size参数通过WordLen进行传递，之后对不同的类型进行判断，调用对应的get方法
    #位
    if datatype==S7WLBit:
        return get_bool(result,0,bit)
    #字节和字
    elif datatype==S7WLByte or datatype==S7WLWord:
        return get_int(result,0)
    #浮点数
    elif datatype==S7WLReal:
        return get_real(result,0)
    #双字
    elif datatype==S7WLDWord:
        return get_dword(result,0)
    else:
        return None
```

主函数调用**ReadMemory**函数，代码如下

```python
def main():
    s71200 = snap7.client.Client()
    connect(s71200, '192.168.2.110', 0, 1)
    while True:
        try:
            #410起始地址，因为是浮点数，所以读取的是MD410
            print(ReadMemory(s71200, 410, 0, S7WLReal))
            sleep(5)
        except Snap7Exception as e:
            connect(s71200, '192.168.2.110', 0, 1)
```

运行结果如下

![](C:\Users\Dave-\Pictures\Snipaste_2019-06-12_17-58-43.png)





## 写M区

写M区跟上一篇写输出寄存器是一样的，都是先通过read_area获取值，通过set方法修改值，之后通过write_area写入值，不同的是，需要按照不同的数据类型，调用不同的set方法。

定义一个**WriteMemory**函数，代码如下

```python
def WriteMemory(dev,byte,bit,datatype,value):
    result = dev.read_area(0x83,0,byte,datatype)
    #不同的数据类型，调用不同的set方法
    if datatype==S7WLBit:
        set_bool(result,0,bit,value)
    elif datatype==S7WLByte or datatype==S7WLWord:
        set_int(result,0,value)
    elif datatype==S7WLReal:
        set_real(result,0,value)
    elif datatype==S7WLDWord:
        set_dword(result,0,value)
    #通过write_area方法写入值到PLC
    dev.write_area(0x83,0,byte,result)
```

主函数调用**WriteMemory**函数，代码如下

```python
def main():
    s71200 = snap7.client.Client()
    connect(s71200, '192.168.2.110', 0, 1)
    while True:
        try:
            print(ReadMemory(s71200, 410, 0, S7WLReal))
            sleep(1)
            #420代表起始地址，这里写入的地址是MD420
            WriteMemory(s71200, 420, 0, S7WLReal, 78.65)
            sleep(1)
            print(ReadMemory(s71200, 420, 0, S7WLReal))
            sleep(5)
        except Snap7Exception as e:
            connect(s71200, '192.168.2.110', 0, 1)
```

运行结果如下

![](C:\Users\Dave-\Pictures\Snipaste_2019-06-12_18-18-23.png)



## 完整代码

```python
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
```

