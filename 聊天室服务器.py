# -*- coding: utf-8 -*-
import  wx
from socket import *
import threading
import time
from concurrent.futures import ThreadPoolExecutor
class MsbServer(wx.Frame):

    def __init__(self):
        '''创建窗口'''
        wx.Frame.__init__(self, None, id=102, title='Patrick9313的服务器界面', pos=wx.DefaultPosition, size=(400, 470))
        pl = wx.Panel(self)  # 在窗口中初始化一个面板
        # 在面板里面会放一些按钮，文本框，文本输入框等，把这些对象统一放入一个盒子里面
        box = wx.BoxSizer(wx.VERTICAL)  # 在盒子里面垂直方向自动排版

        g1 = wx.FlexGridSizer(wx.HORIZONTAL)  # 可升缩的网格布局,水平方向
        # 创建三个按钮
        start_server_button = wx.Button(pl, size=(133, 40), label="启动")
        record_save_button = wx.Button(pl, size=(133, 40), label="聊天记录保存")
        stop_server_button = wx.Button(pl, size=(133, 40), label="停止")
        g1.Add(start_server_button, 1, wx.TOP )
        g1.Add(record_save_button, 1, wx.TOP )
        g1.Add(stop_server_button, 1, wx.TOP )
        box.Add(g1, 1, wx.ALIGN_CENTER)  # ALIGN_CENTER 联合居中

        # 创建只读的文本框,显示聊天记录
        self.text = wx.TextCtrl(pl, size=(400, 400), style=wx.TE_MULTILINE | wx.TE_READONLY)
        box.Add(self.text, 1, wx.ALIGN_CENTER)
        pl.SetSizer(box)
        '''以上代码窗口结束 '''
        # 创建一个拥有10个工作线程的线程池
        self.executor = ThreadPoolExecutor(max_workers=10)

        '''服务准备执行的一些属性'''
        self.isOn = False # 服务器没有启动
        self.host_port= ('',8888)
        self.server_socket = socket(AF_INET,SOCK_STREAM) # TCP协议的服务器端套接字
        self.server_socket.bind(self.host_port)
        self.server_socket.listen(5)
        self.session_thread_map={} # 存放所有的服务器会话线程，字典：客户端名字为Key，会话线程为Value

        '''给所有的按钮绑定相应的动作'''
        self.Bind(wx.EVT_BUTTON,self.start_server,start_server_button) #给启动按钮，绑定一个按钮事件，事件触发的时候会自动调用一个函数
        self.Bind(wx.EVT_BUTTON,self.save_record,record_save_button)


    #服务器开始启动函数
    def start_server(self,event):
        print('服务器开始启动')
        if not self.isOn:
            #启动服务器的主线程
            self.isOn =True
            main_thread = threading.Thread(target=self.do_work)
            main_thread.setDaemon(True) #设置为守护线程
            main_thread.start()

    #服务运行之后的函数
    def do_work(self):
        print("服务器开始工作")
        while self.isOn:
            session_socket,client_addr = self.server_socket.accept()
            #服务首先接受客户端发过来的第一条消息，我们规定第一条消息为客户端的名字
            username = session_socket.recv(1024).decode('UTF-8') #接受客户端名字
            #创建一个会话线程
            session_thread =  SessionThread(session_socket,username,self)
            self.session_thread_map[username] = session_thread
            # 使用线程池处理连接
            self.executor.submit(session_thread.run)
            # 表示有客户端进入到聊天室
            self.show_info_and_send_client("服务器通知","欢迎%s进入聊天室！"%username,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
        self.server_socket.close()


    #在文本中显示聊天信息，同时发送消息给所有客户端 ,source：信息源，data就是信息，
    def show_info_and_send_client(self,source,data,data_time):
        send_data = '%s : %s\n时间：%s\n' %(source,data,data_time)
        self.text.AppendText('---------------------------------\n%s' %send_data) #在服务器的文本框显示信息
        for client in self.session_thread_map.values():
            if client.isOn: #当前客户端是活动
                client.user_socket.send(send_data.encode('UTF-8'))

    #服务保存聊天记录
    def save_record(self,event):
        record = self.text.GetValue()
        with open("record.log","w+") as f:
            f.write(record)


# 服务器端会话线程的类
class SessionThread(threading.Thread):
    def __init__(self,socket,un,server):
        threading.Thread.__init__(self)
        self.user_socket=socket
        self.username =un
        self.server =server
        self.isOn = True # 会话线程是否启动

    def run(self): # 会话线程的运行
        print('客户端%s,已经和服务器连接成功，服务器启动一个会话线程'%self.username)
        while self.isOn:
            data = self.user_socket.recv(1024).decode('UTF-8') #接受客户端的聊天信息
            if data == 'A^disconnect^B': # 如果客户端点击断开按钮，先发一条消息给服务器：消息的内容我们规定：A^disconnect^B
                self.isOn = False
                # 有用户离开，需要在聊天室通知其他人
                self.server.show_info_and_send_client("服务器通知","%s离开聊天室！"%self.username,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
            else:
                # 其他聊天信息，我们应该显示给所有客户端，包括服务器
                self.server.show_info_and_send_client(self.username,data,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
        self.user_socket.close() # 保持和客户端会话的socket关掉

if __name__ == '__main__':
    app = wx.App()
    MsbServer().Show()
    app.MainLoop()  # 循环刷新显示