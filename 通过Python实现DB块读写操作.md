## 通过Python实现DB区读写操作(一)

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
DB005 Real 264.0
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

### 定义DBRead()函数

这里希望DBRead函数中的参数如下代码所示：

```python
def DBRead(dev,db_num,db_len,db_items):
```

dev参数是设备名称，db_num是DB块编号，db_len是DB块中所有数据总长度，db_items是DB块中数据，它的数据结构应该和上图所示的字典列表一致。

首先通过**read_area**获取DB块中的数据，代码如下

```python
data = plc.read_area(0x84,db_num,0,db_len):
```

通过**for**循环以此取出db_items中的字典，通过键判断数据类型和偏移量，之后调用对应的get方法，代码如下

```python
for item in db_items:
        value = None
        #取出数据的偏移量
        offset = int(item['bytebit'].split('.')[0])
		#通过键datatype获取数据类型，调用不同的get方法
        if item['datatype']=='Real':
            value = get_real(data,offset)

        if item['datatype']=='Bool':
            bit =int(item['bytebit'].split('.')[1])
            value = get_bool(data,offset,bit)

        if item['datatype']=='Int':
            value = get_int(data, offset)

        if item['datatype']=='String':
            value = get_string(data, offset)
```

完整**DBRead**函数的代码如下

```python
def DBRead(dev,db_num,db_len,db_items):
    data = dev.read_area(0x84,db_num,0,db_len)
    obj = DBObject()
    for item in db_items:
        value = None
        offset = int(item['bytebit'].split('.')[0])

        if item['datatype']=='Real':
            value = get_real(data,offset)

        if item['datatype']=='Bool':
            bit =int(item['bytebit'].split('.')[1])
            value = get_bool(data,offset,bit)

        if item['datatype']=='Int':
            value = get_int(data, offset)

        if item['datatype']=='String':
            value = get_string(data, offset)

        obj.__setattr__(item['name'], value)

    return obj
```

DBRead函数中还需要知道db_len的值，所以还需要定义一个函数去获得DB块中数据的总长度

### 定义get_db_len()函数

通过下图

![1560418884428](C:\Users\Dave-\AppData\Roaming\Typora\typora-user-images\1560418884428.png)

可以看出，数据的总长度其实就是最后一个数据的偏移量的数值加上自生所占的数据长度，如图五个数据的总长度应该是**264 + 4 = 268**，所以get_db_len()函数只要找到偏移量最大的数，在获得这个偏移量对用的数据类型所占的内存长度，相加后就可以得到整个数据长度。

```python
def get_db_len(db_items,bytebit,datatype):
```

**db_items**和DBRead函数中的一致，**bytebit**和**datatype**是db_items中字典的两个键名，通过

```python
offset_str,datatype =[(x[bytebit]) for x in db_items],[x[datatype] for x in db_items]
```

获得偏移量和数据类型的列表，结果应该如下

```python
offset_str = ['0.0','4.0','6.0','8.0','264.0'],datatype = [Real,Bool,Int,String,Real]
```

因为获取的offset值均为字符串，所有没法正确获取最大值，需要将字符串列表转换为整数的列表，代码如下

```python
for x in offset_str:
	offset_int.append(int(x.split('.')[0]))
```

之后通过**index**方法获得offset中最大值的索引值，通过此索引值获得datatype列表中的数据类型，代码如下

```python
idx = offset_int.index(max(offset_int)) #结果=4
```

为了得到不同数据类型占用内存的长度，需要先定义一个字典，可以通过不同的数据类型取出对应的内存长度，如下

```python
offsets = { "Bool":2,"Int": 2,"Real":4,"DInt":6,"String":256}
```

之后便可获得DB块中数据总长度，如下

```python
db_len = (max(offset_int)) + int(offsets[datatype[idx]]) #结果=264+4=268
```

完整的**get_db_len()**函数如下

```python
def get_db_len(db_items,bytebit,datatype):
    offset_int = []
    offset_str,datatype =[(x[bytebit]) for x in db_items],[x[datatype] for x in db_items]
    for x in offset_str:
        offset_int.append(int(x.split('.')[0]))
    idx = offset_int.index(max(offset_int)) #结果=4
    db_len = (max(offset_int)) + int(offsets[datatype[idx]]) #结果=264+4=268
    return db_len
```

至此，两个函数全部定义完了，接下来需要在主函数中构造db_items列表

### 主函数

通过如下的代码构造db_items列表

```python
itemlist = filter(lambda a: a!='',db.split('\n'))
    space=''
    items = [
        {
            "name":x.split(space)[0],
            "datatype":x.split(space)[1],
            "bytebit":x.split(space)[2]
         } for x in itemlist
    		]
```

通过上面的两个函数获得DB块中的数据

```python
db_len = get_db_len(items, 'bytebit', 'datatype')
DB_obj = DBRead(s71200, 1, db_len, items)
print(DB_obj.DB001, DB_obj.DB002, DB_obj.DB003, DB_obj.DB004, DB_obj.DB005)
sleep(5)
```

最终结果如下

![](H:\snap7ForS71200\Snipaste_2019-06-14_20-17-21.png)

## 完整代码

```python
from time import sleep
import snap7
from snap7.snap7exceptions import Snap7Exception
from snap7.util import *

db = \
"""
DB001 Real 0.0
DB002 Bool 4.0
DB003 Int 6.0
DB004 String 8.0
DB005 Real 264.0
"""

offsets = { "Bool":2,"Int": 2,"Real":4,"DInt":6,"String":256}

class DBObject(object):
    pass


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


def DBRead(dev,db_num,db_len,db_items):
    data = dev.read_area(0x84,db_num,0,db_len)
    obj = DBObject()
    for item in db_items:
        value = None
        offset = int(item['bytebit'].split('.')[0])

        if item['datatype']=='Real':
            value = get_real(data,offset)

        if item['datatype']=='Bool':
            bit =int(item['bytebit'].split('.')[1])
            value = get_bool(data,offset,bit)

        if item['datatype']=='Int':
            value = get_int(data, offset)

        if item['datatype']=='String':
            value = get_string(data, offset, 256)

        obj.__setattr__(item['name'], value)

    return obj

def get_db_len(db_items,bytebit,datatype):
    offset_int = []
    offset_str,datatype =[(x[bytebit]) for x in db_items],[x[datatype] for x in db_items]
    for x in offset_str:
        offset_int.append(int(x.split('.')[0]))
    idx = offset_int.index(max(offset_int)) #结果=4
    db_len = (max(offset_int)) + int(offsets[datatype[idx]]) #结果=264+4=268
    return db_len

def main():
    s71200 = snap7.client.Client()
    connect(s71200, '192.168.2.111', 0, 1)
    while True:
        try:
            itemlist = filter(lambda a: a != '', db.split('\n'))
            space = ' '
            items = [
                {
                    "name": x.split(space)[0],
                    "datatype": x.split(space)[1],
                    "bytebit": x.split(space)[2]
                } for x in itemlist
            ]
            db_len = get_db_len(items, 'bytebit', 'datatype')
            DB_obj = DBRead(s71200, 1, db_len, items)
            print(DB_obj.DB001, DB_obj.DB002, DB_obj.DB003, DB_obj.DB004, DB_obj.DB005)
            sleep(5)
        except Snap7Exception as e:
            connect(s71200, '192.168.2.111', 0, 1)

if __name__ == '__main__':
    main()
```

