# -*- coding: utf-8 -*-
import wx
from socket import *
import threading

# 客户端继承 wx.Frame，就拥有窗口界面
class MsbClient(wx.Frame):
    def __init__(self,c_name): #c_name:客户端名字
        #调用父类的初始化函数
        wx.Frame.__init__(self,None,id=101,title='%s的客户端界面'%c_name,pos=wx.DefaultPosition,size=(400,470))
        pl = wx.Panel(self) # 在窗口中初始化一个面板
        #在面板里面会放一些按钮，文本框，文本输入框等，把这些对象统一放入一个盒子里面
        box = wx.BoxSizer(wx.VERTICAL) # 在盒子里面垂直方向自动排版

        g1 = wx.FlexGridSizer(wx.HORIZONTAL)  #可升缩的网格布局,水平方向
        #创建两个按钮
        conn_button = wx.Button(pl,size=(200,40),label= "连接")
        dis_conn_button = wx.Button(pl,size=(200,40),label= "离开")
        g1.Add(conn_button,1, wx.TOP | wx.LEFT) # 连接按钮布局在左边
        g1.Add(dis_conn_button,1, wx.TOP | wx.RIGHT) # 断开按钮布局在右边
        box.Add(g1,1,wx.ALIGN_CENTER) # ALIGN_CENTER 联合居中


        #创建聊天内容的文本框，不能写消息 :TE_MULTILINE -->多行  TE_READONLY-->只读
        self.text =  wx.TextCtrl(pl,size=(400,250),style =wx.TE_MULTILINE | wx.TE_READONLY)
        box.Add(self.text,1,wx.ALIGN_CENTER)

        #创建聊天的输入文本框,可以写
        self.input_text = wx.TextCtrl(pl, size=(400, 100), style=wx.TE_MULTILINE )
        box.Add(self.input_text, 1, wx.ALIGN_CENTER)

        #最后创建两个按钮，分别是发送和重置
        g2 = wx.FlexGridSizer(wx.HORIZONTAL)
        clear_button = wx.Button(pl, size=(200, 40), label="重置")
        send_button = wx.Button(pl, size=(200, 40), label="发送")
        g2.Add(clear_button,1,wx.TOP | wx.LEFT)
        g2.Add(send_button,1,wx.TOP | wx.RIGHT)
        box.Add(g2,1,wx.ALIGN_CENTER)


        pl.SetSizer(box) #把盒子放入面板中

        ''' 以上代码完成了客户端界面（窗口） '''

        '''给所有按钮绑定点击事件'''
        self.Bind(wx.EVT_BUTTON,self.connect_to_server,conn_button)
        self.Bind(wx.EVT_BUTTON,self.send_to,send_button)
        self.Bind(wx.EVT_BUTTON,self.go_out,dis_conn_button)
        self.Bind(wx.EVT_BUTTON,self.reset,clear_button)

        '''客户端的属性'''
        self.name =c_name
        self.isConnected = False #客户端是否已经连上服务器
        self.client_socket = None


    # 连接服务器
    def connect_to_server(self,event):
        print("客户端%s,开始连接服务器"%self.name)
        if not self.isConnected:
            server_host_port = ('localhost',8888)
            self.client_socket = socket(AF_INET,SOCK_STREAM)
            self.client_socket.connect(server_host_port)
            # 之前规定，客户端只要连接成功，马上把自己的名字发给服务器
            self.client_socket.send(self.name.encode('UTF-8'))
            t  = threading.Thread(target=self.receive_data)
            t.setDaemon(True) # 客户端UI界面如果关闭，当前守护线程也自动关闭
            self.isConnected = True
            t.start()

    # 接受服务器发送过来的聊天数据
    def receive_data(self):
        print("客户端准备接收服务器的数据")
        while self.isConnected:
            data =self.client_socket.recv(1024).decode('UTF-8')
            # 从服务器接收到的数据，需要显示
            self.text.AppendText('%s\n'%data)


    #客户端发送信息到聊天室
    def send_to(self,event):
        if self.isConnected:
            info = self.input_text.GetValue()
            if info != '':
                self.client_socket.send(info.encode('UTF-8'))
                #输入框中的数据如果已经发送了，输入框重新为空
                self.input_text.SetValue('')

    # 客户端离开聊天
    def go_out(self,event):
        self.client_socket.send('A^disconnect^B'.encode('UTF-8'))
        # 客户端主线程也关闭
        self.isConnected = False


    # 客户端输入框的信息重置
    def reset(self,event):
        self.input_text.Clear()

if __name__ == '__main__':
    app = wx.App()
    name = input("请输入客户端名字:")
    MsbClient(name).Show()
    app.MainLoop() #循环刷新显示

