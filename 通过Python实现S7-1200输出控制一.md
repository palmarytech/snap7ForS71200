## 通过Python实现S7-1200输出控制

*版权声明*
*无需授权随便转载*

## Snap7

Snap7是一个开源的，支持32位和64位跨平台的通讯包组件，可以实现与西门子系列PLC进行数据读写操作，目前支持的PLC包括1200/1500，S7200，LOGO等。

这个通讯包的好处显而易见，首先跨平台就可以实现在运行Linux的平台上进行与PLC的通讯，最常见的就是使用**Raspberry PI**控制PLC，而且使用这个通讯包也可以定制自己的软件，实现对PLC的读写操作，目前我主要是通过LabVIEW和C#控制PLC，后面我都会讲到。

## Python-Snap7

在讲这些之前，我发现网上已经有人把Snap7封装成了Python可以使用的组件，鉴于Python的流行度和易用性，我准备先从Python开始介入这款驱动，这些内容的主要目的还是给大家提供一种选择，具体的做法还得靠大家自己根据实际的需要慢慢研究。

这里我使用的Python开发环境是Pycharm，具体使用方法我就不说了，大家自己研究吧，网上的帖子也很多。

使用之前，需要将snap7.dll文件拷贝到系统路径下，如果是32位系统拷贝到*C:\WINDOW\system32*下面，如果是64位系统需要拷贝到*C:\Windows\sysWOW64*下面，Snap7最新的组件包可以通过*http://sourceforge.net/projects/snap7/files/*网址下载，当然点击阅读原文也可以从我提供的地址下载。

之后还需要下载用于Python的Snap7，使用Pycharm作为开发环境，可以直接再Pycharm内下载并且安装Python-snap7，这些都准备好了，就可以开始编写代码了。Python-Snap7的官方网址*https://python-snap7.readthedocs.io/*

PLC的环境还是使用TIA v14运行模拟器，通过NetToPLCsim连接PLCsim实现。具体的做法可以参考上一篇文章。



## 读输出映像区-Q区

在进行读写操作之间，需要创建一个Client

```python
s71200 = snap7.client.Client()
```

创建Client之后，通过**connect**方法进行连接，connect方法定义如下

```python
def connect(self, address, rack, slot, tcpport=102)
```

其中**address**是服务器的IP地址，如果使用NetToPLCsim连接PLCsim，则IP地址应该是计算机的IP地址，**rack**和**slot**和NetToPLCsim设置的一样，针对S7-1200此处应该是0和1，端口默认是102，不需要进行更改

连接后可以通过**get_connected**检查连接是否建立，返回值如果是True，则代表连接成功

连接建立后，通过**read_area**方法获取PLC各个区的数值，read_area方法定义如下

```python
def read_area(self, area, dbnumber, start, size)
```

**area**是PLC内各寄存区的代码，具体参考下表

![1560245900700](C:\Users\Dave-\AppData\Roaming\Typora\typora-user-images\1560245900700.png)

**dbnumber**只针对DB块才有效，**start**为寄存区起始地址，**size**是读取数量

读取输出映像区时，具体的参数如下

```python
read_area(0x82, 0, 0, 1)
```

**read_area**的返回值是**bytearray**类型，需要转换成2进制类型

完整代码如下

```python
import snap7
from snap7.snap7exceptions import Snap7Exception
from time import sleep

def connect(device, ip, rack, slot):
    while True:
        # check connection
        if device.get_connected()://如果
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
```

输出的结果

```python
[1, 0, 0, 0, 0, 0, 1, 0]
```

![1560248366116](C:\Users\Dave-\AppData\Roaming\Typora\typora-user-images\1560248366116.png)
