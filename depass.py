#-*- coding: utf-8 -*-

from pykeyboard import PyKeyboard
import itertools
import time
import tkinter as tk
import tkinter.messagebox
import threading
import inspect
import ctypes
import win32con
import ctypes.wintypes
import pygame,os,sys
from tkinter import ttk


global T1,T2                                                                    #T1存放brute线程，T2存放进度条线程
global maximum
global start,end,sleep,step                 
 
maximum = 200                                                                   #进度条最大刻度
window = tk.Tk()
k = PyKeyboard()
SLEEP=tk.DoubleVar()                                                            #与scale绑定

GO=False                                                                        #用来传递爆破的参数
STOP=False                                                                      #用来传递停止爆破的参数
EXIT = False                                                                    #用来传递退出程序的参数
user32 = ctypes.windll.user32                                                   #加载user32.dll

#注册热键的唯一id，用来区分热键
id1=109                                                                         #F1 (brute)          
id2=110                                                                         #F2 (stop brute)
id3=111                                                                         #F3 (stop program)


def __start_end():                                                              #获取输入的start和end
    global start,end,step
    start = int(START.get())                                     
    end = int(END.get())
    step = maximum / (end - start +1)                                           #计算进度条每次前进走的格数
    return
def start_end():
    T = threading.Thread(target=__start_end)
    T.setDaemon(True)                                                           #设为守护线程，父线程（此处为主程序）退出后，所有守护线程退出
    T.start()


def __interval():                                                               #设置每次爆破时间间隔
    global sleep
    sleep = SLEEP.get()
    return
def interval(self):
    T = threading.Thread(target=__interval)
    T.setDaemon(True)
    T.start()


def __brute():                                                                  #开始爆破
    global sleep,start,end
    ns = itertools.count(start)                                                 #重置迭代器   #start from here，ns为原始序列
    j = itertools.takewhile(lambda x:x<=end,ns)                                 #to here,j为截取序列序列
    time.sleep(3)                                                               #3秒延时后爆破
    progress()                                                                  #开始推动进度条
    for i in j:
        time.sleep(sleep)
        k.type_string(str(i))
        time.sleep(0.001)                                                       #按键间隔                              
        k.tap_key(k.enter_key)
        # print(p1['value'])
    return
def brute():
    global T1
    T1 = threading.Thread(target=__brute)
    T1.setDaemon(True)
    T1.start()


def __stop_thread(thread):
    _async_raise(thread.ident, SystemExit)
def stop_thread():                          
    __stop_thread(T1)                                                           #终止brute线程
    __stop_thread(T2)                                                           #终止进度条线程
    p1['value'] = 0                                                             #重置进度条


def __monitor():                                                                #监视热键是否被激活
    global GO,STOP,EXIT
    while(True):
        if GO==True:
            #这里是用于开始爆破的
            brute()
            GO=False
        elif STOP==True:
            #这里是用于停止爆破的
            stop_thread()
            STOP=False
        elif EXIT==True:
            #这里是用于退出程序的
            window.destroy()
def monitor():
    T = threading.Thread(target=__monitor)                                      #创建监听热键的线程
    T.setDaemon(True)
    T.start()


def __playSans():                                                               #播放sound
    pygame.mixer.init()                                                         #初始化声音播放模块
    APP_FOLDER = os.path.dirname(os.path.realpath(sys.argv[0]))                 #读取当前工作目录   
    os.chdir(APP_FOLDER)                                                        #改变当前工作目录
    pygame.mixer.music.load("sans.ogg")                                         #导入ogg
    pygame.mixer.music.play(-1, 0)                                              #-1表示循环，从0秒处开始播放
def playSans():
    T = threading.Thread(target=__playSans)                                     #创建播放线程
    T.setDaemon(True)
    T.start() 


def __progress():                                                               #推进进度条
    num = end - start + 1                                                       #一次爆破num个code          
    for i in range(1, num + 1):
        time.sleep(0.023)
        time.sleep(sleep)
        p1.step(step)
        window.update()    
    p1['value'] = maximum
    # for i in range(start,end+1):
    #     p1['value'] = i
    #     window.update()
    #     #print(i)
    #     time.sleep(sleep)
def progress():                                                                 #创建进度条子线程
    global T2
    T2 = threading.Thread(target=__progress)
    T2.setDaemon(True)                                                          #设为守护线程，父线程（此处为主程序）退出后，所有守护线程退出
    T2.start()


def _async_raise(tid, exctype):                                                 #终止线程的函数
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def closeWindow():                                                              #点击x是询问是否退出
    ans = tk.messagebox.askyesno(title='Warning',message='Close the application?',default='no')
    if ans:
        window.destroy()
    else:
        return

class Hotkey(threading.Thread):                                                 #创建一个Thread.threading的扩展类  

    def run(self):  
        global GO,STOP,EXIT                                                     #定义全局变量，这个可以在不同线程间共用。

        if not user32.RegisterHotKey(None, id1, 0, win32con.VK_F1):             # 注册快捷键F1并判断是否成功，该热键用于开始爆破 
            print ("Unable to register id"), id1                                # 返回一个错误信息

        if not user32.RegisterHotKey(None, id2, 0, win32con.VK_F2):             # 注册快捷键F2并判断是否成功，该热键用于结束爆破
            print ("Unable to register id"), id2

        if not user32.RegisterHotKey(None, id3, 0, win32con.VK_F3):             # 注册快捷键F3并判断是否成功，该热键用于结束程序
            print ("Unable to register id"), id3

        #以下为检测热键是否被按下，并在最后释放快捷键  
        try:  
            msg = ctypes.wintypes.MSG()  

            while True:
                if user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:

                    if msg.message == win32con.WM_HOTKEY:  
                        if msg.wParam == id1:                                   #激活热键
                            GO = True
                        elif msg.wParam == id2:
                            STOP = True
                        elif msg.wParam == id3:
                            EXIT = True

                    user32.TranslateMessage(ctypes.byref(msg))  
                    user32.DispatchMessageA(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, id1)                                  #必须得释放热键，否则下次就会注册失败，所以当程序异常退出，没有释放热键，
                                                                                #那么下次很可能就没办法注册成功了，这时可以换一个热键测试
            user32.UnregisterHotKey(None, id2)

            user32.UnregisterHotKey(None, id3)



monitor()                                                                       #监听热键
playSans()                                                                      #播放sans

hotkey = Hotkey()                                                               #创建热键线程
hotkey.setDaemon(True)
hotkey.start()


window.protocol('WM_DELETE_WINDOW', closeWindow)                                #接受到点击关闭时调用函数closeWindow

#以下为gui界面

window.title('password bruter')
window.geometry('600x360')                                                      #设置分辨率
l = tk.Label(window, text="Brute every 'sleep' seconds from 'start' to 'end' which you set BELOW", font=('Arial', 11, 'bold'), width=100, height=2)
l.pack()                                                                        #标题
m = tk.Label(window, text="Press 'F3' to quit the program! ! !", font=('Arial', 11, 'bold'), width=50, height=1, underline='8')
m.pack()  
stitle = tk.Label(window, text='start')
stitle.pack()
START = tk.Entry(window, cursor='plus', width=15)                               #start输入文本框
START.pack()
etitle = tk.Label(window, text='end')
etitle.pack()
END = tk.Entry(window, cursor='plus', width=15)                                 #end输入文本框
END.pack()


b1 = tk.Button(window, text='ok', width=14, height=1, command=start_end)        #按钮b1
b1.pack()
s = tk.Scale(window, label='select sleep interval', cursor='circle', sliderrelief='raised', sliderlength=50, tickinterval=0.2, bd=5, from_=0, to=1, resolution=0.001, orient=tk.HORIZONTAL, length=400, variable=SLEEP, command=interval)
s.pack()                                                                        #设置sleep间隔滑块

p1 = ttk.Progressbar(window, length=400, orient=tk.HORIZONTAL, mode='determinate')
p1.pack()
p1['maximum'] = maximum         
b2 = tk.Button(window, text='start blasting(F1)', width=15, height=1, underline=16, command=brute)
b2.pack(side='left', anchor='w', padx=50)                                       #按钮b2,开始爆破
b3 = tk.Button(window, text='stop blasting(F2)', width=15, height=1, underline=15, command=stop_thread)
b3.pack(side='right', anchor='e', padx=50)                                      #按钮b3,停止进程

window.mainloop()