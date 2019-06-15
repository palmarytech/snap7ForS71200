# 通过LabVIEW实现Q区读操作

## 引子

之前写了几篇通过Python访问PLC的文章，但是实际工程应用中，python并不是自动化工程师的首选工具，对于数据分析，python确实很好用，但是对于实际工程应用，LabVIEW可能更胜一筹。但是为什么先通过Python说起呢，因为python语法结构简单清晰，可以很容易明白驱动的使用逻辑，对于后续通过C#和LabVIEW的访问会有一些帮助，从今天开始，我会使用LabVIEW搭配Sanp7来实现对S7-1200PLC的各个寄存去的读写操作。

## .Net Connectivity

之前LabVIEW和Matlab混合编程的文章中我介绍过这种方法，没有看过的小伙伴可以翻一翻之前的文章，snap7同样有一个编译好的.Net组件，它的路径如下

```c
snap7-full-1.4.2\examples\dot.net\WinForm\BuildSnap7Assembly\bin
```

bin文件夹有针对64位和32位两个dll文件，这里我的操作系统是Win10 64位专业版，LabVIEW是64位2018版，所以我选在的是64位的**Snap7.net.dll**文件，Snap7所有的属性和方法全部都编译到了这个.Net文件中，我们可以通过LabVIEW的**.Net Connectivity**选项板下面的vi工具来使用这个.Net组件

## 建立连接

.Net Connectivity选项板位于如图所示的位置

![](C:\Users\dave-\OneDrive\图片\Snipaste_2019-06-15_09-49-29.png)

标红框的是需要用的几个vi，先使用**Constructor Node**，弹出**Select .Net Constructor**的对话框，点击Brower，选择对应的Snap7.net.dll文件，之后Object框里就会出现所有方法，这里选择S7Client方法，他的返回是一个S7Object，这里可以理解为**对类的实例化**，只要有了这个实例化对象，接下来就可以使用类的所有属性和方法

![](C:\Users\dave-\OneDrive\图片\Snipaste_2019-06-15_09-51-56.png)

下图是Snap7中**Cli_Create()**的描述

![1560564124974](C:\Users\dave-\AppData\Roaming\Typora\typora-user-images\1560564124974.png)

实例化之后，需要调用一个ConnectTo方法来实现对PLC的连接，LabVIEW中使用**Invoke Node**来使用对象的方法

![1560564359394](C:\Users\dave-\AppData\Roaming\Typora\typora-user-images\1560564359394.png)

将之前实例化的Client对象通过连线和**Invoke Node**连起来，就能看到**Method**的选择项。

![1560565220194](C:\Users\dave-\AppData\Roaming\Typora\typora-user-images\1560565220194.png)

点击**Method**，找到**ConnectTo**方法

![](C:\Users\dave-\OneDrive\图片\Snipaste_2019-06-15_10-21-50.png)

下图是ConnectTo方法各个参数的含义，这些参数在Python访问PLC的文章中都有过介绍

![1560565376532](C:\Users\dave-\AppData\Roaming\Typora\typora-user-images\1560565376532.png)

如果连接正确，则返回值是0，如果连接错误，就会返回对应的错误代码，LabVIEW中的连接如下图

![1560565570236](C:\Users\dave-\AppData\Roaming\Typora\typora-user-images\1560565570236.png)

点击运行后，如果和PLC连接上了，则ConnectOK？的返回值就是0，如下图

![](H:\snap7ForS71200\connectOK.gif)

## 读Q区

读Q区的数据，需要使用Cli_ReadArea方法，这个方法在之前的Python的文章中介绍过，这里不再赘述，下图是此方法的参数

![1560572637668](H:\snap7ForS71200\1560572637668.png)

Client参数是实例化的对象，Area填入0x82，DBnumber只针对DB块，Start是起始地址，Amount是访问的数据数量，Wordlen参数参看下表

![1560572778885](H:\snap7ForS71200\1560572778885.png)

pUserData参数是存放数据的缓冲区指针变量，此方法的返回值如果是0，则表示读数据成功，读回来的数据已十进制显示，可以通过**Number To BoolArray**方法转换成布尔变量，与PLC的Q区对应。LabVIEW的框图如下

![](H:\snap7ForS71200\Snipaste_2019-06-15_12-49-27.png)

最终的效果如下图

![](H:\snap7ForS71200\readQ.gif)

## 写Q区

写Q区的数据，需要使用Cli_WriteArea方法，这个方法在之前的Python的文章中也介绍过，这里不再赘述，下图是此方法的参数

![1560590683609](H:\snap7ForS71200\1560590683609.png)

唯一的不同是需要将写入的数据放到pUserData数组中，这里使用**Boolean Array To Number**将布尔量转换成十进制数，在构建pUserData数组传递给WriteArea方法

LabVIEW的框图如下图

![1560590812642](H:\snap7ForS71200\1560590812642.png)

最终效果如下图

![](H:\snap7ForS71200\writeQ.gif)