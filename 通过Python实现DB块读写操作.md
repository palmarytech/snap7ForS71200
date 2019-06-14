## 通过Python实现M区读写操作

*版权声明*

*无需授权随便转载*



## 读DB区

使用的方法依旧是read_area

```python
def read_area(self, area, dbnumber, start, size)
```

**area**是PLC内各寄存区的代码，具体参考下表

![1560245900700](C:\Users\Dave-\AppData\Roaming\Typora\typora-user-images\1560245900700.png)

**dbnumber**是DB块编号，可以在DB块属性中常规选项中查看到，**start**为寄存区起始地址，**size**是DB块完整的长度，因为DB块中可以有各种数据类型，所以长度参数一定要准确，否则返回数据会出现问题。

要访问DB块，必须取消DB块属性中的**优化的块访问**选项

针对的是DB块，所有area参数需要使用**0x84**，size参数需要通过DB块内的数据数量和数据类型具体计算出来

因为read_area方法返回的是byteArray类型的结果，可以通过get_bool，get_int，get_read，get_dword方法直接将byteArray类型转换成对应的数据类型

比如针对get_bool方法

```python
def get_bool(_bytearray, byte_index, bool_index)
```

第一个**bytearray**参数是read_area的返回值，**byte_index**参数是DB块中变量的**偏移量**，bool_index参数是位变量的地址。

先来看一个简单的例子，DB块中有两个变量，一个浮点数，一个布尔量

![1560418256183](C:\Users\Dave-\AppData\Roaming\Typora\typora-user-images\1560418256183.png)

main函数中的代码如下

```python
def main():
    s71200 = snap7.client.Client()
    connect(s71200, '192.168.2.110', 0, 1)
    while True:
        try:
            data = s71200.read_area(0x84, 1, 0, 5)#此处5代表DB块中数据长度，浮点数4个byte，布尔量一个byte
            print(data)
            value = get_real(data, 0)#此处0是浮点数的偏移量
            value2 = get_bool(data, 4, 0)#此处4是布尔量的偏移量
            print(value, value2)
            sleep(5)
        except Snap7Exception as e:
            connect(s71200, '192.168.2.110', 0, 1)

if __name__ == '__main__':
    main()
```

运行后如下

![1560418396496](C:\Users\Dave-\AppData\Roaming\Typora\typora-user-images\1560418396496.png)

但是这样操作很麻烦，需要提前计算好DB块中的数据长度，需要将每个数据的偏移量和数据类型都填好，这里希望有一个简单的方法，定义好DB块的数据名称，数据类型，数据偏移量，之后运行程序后，自动计算长度，对应数据类型和偏移量，从而获取正确的结果。

DB块中的数据名称及数据类型，偏移量如下图

![1560418884428](C:\Users\Dave-\AppData\Roaming\Typora\typora-user-images\1560418884428.png)

### 定义DB块数据格式

```python
db = \
"""
DB001 Real 0.0
DB002 Bool 4.0
DB003 Int 6.0
DB004 String 8.0
DB005 Real 264
"""
```

数据格式定义好后，需要从这个数据格式中得到read_area方法要的参数，这里通过字典是很容易实现的，我们可以定义一个字典的列表，列表中每一个字典都是一个数据，字典的键值可以是**name**，**datatype**，**bytebit**，数据结构如下

```python
[
{'name': 'DB001', 'datatype': 'Real', 'bytebit': '0.0'},
{'name': 'DB002', 'datatype': 'Bool', 'bytebit': '4.0'},
{'name': 'DB003', 'datatype': 'Int', 'bytebit': '6.0'},
{'name': 'DB004', 'datatype': 'String', 'bytebit': '8.0'}
{'name': 'DB005', 'datatype': 'Real', 'bytebit': '264'}    
]
```

之后可以通过for方法依次取出每一个键值，传递到read_area方法中。

### 定义DBRead函数



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

