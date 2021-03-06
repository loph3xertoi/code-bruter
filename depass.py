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

global T1,T2
window = tk.Tk()
k = PyKeyboard()
SLEEP=tk.DoubleVar()                                             #与scale绑定

GO=False                                                                    #用来传递爆破的参数
STOP=False                                                                  #用来传递停止爆破的参数
EXIT = False                                                                #用来传递退出程序的参数
user32 = ctypes.windll.user32                            #加载user32.dll

#注册热键的唯一id，用来区分热键
id1=109                                                                      #F1 (brute)          
id2=110                                                                      #F2 (stop brute)
id3=111                                                                      #F3 (stop program)

def __start_end():                                                 #获取输入的start和end
    global start,end
    start = int(START.get())                                     
    end = int(END.get())
    return

def __interval():                                              #设置每次爆破时间间隔
    global sleep
    sleep = SLEEP.get()
    return


def __brute():                                                     #开始爆破
    global sleep,start,end
    ns = itertools.count(start)                                  #重置迭代器   #start from here，ns为原始序列
    j = itertools.takewhile(lambda x:x<=end,ns)                  #to here,j为截取序列序列
    time.sleep(1)
    for i in j:
        time.sleep(sleep)
        k.type_string(str(i))
        time.sleep(0.001)                                       #参数1
        k.tap_key(k.enter_key)
    return

def start_end():
    T = threading.Thread(target=__start_end)
    T.setDaemon(True)                                           #设为守护线程，父线程（此处为主程序）退出后，所有守护线程退出
    T.start()

def interval(self):
    T = threading.Thread(target=__interval)
    T.setDaemon(True)
    T.start()

def brute():
    global T1
    T1 = threading.Thread(target=__brute)
    T1.setDaemon(True)
    T1.start()

def _async_raise(tid, exctype):
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

def __stop_thread(thread):
    _async_raise(thread.ident, SystemExit)

def stop_thread():                  #终止brute线程
    __stop_thread(T1)




class Hotkey(threading.Thread):  #创建一个Thread.threading的扩展类  

    def run(self):  
        global GO,STOP,EXIT  #定义全局变量，这个可以在不同线程间共用。

        if not user32.RegisterHotKey(None, id1, 0, win32con.VK_F1):   # 注册快捷键F1并判断是否成功，该热键用于开始爆破 
            print ("Unable to register id"), id1 # 返回一个错误信息

        if not user32.RegisterHotKey(None, id2, 0, win32con.VK_F2):   # 注册快捷键F2并判断是否成功，该热键用于结束爆破
            print ("Unable to register id"), id2

        if not user32.RegisterHotKey(None, id3, 0, win32con.VK_F3):   # 注册快捷键F3并判断是否成功，该热键用于结束程序
            print ("Unable to register id"), id3

        #以下为检测热键是否被按下，并在最后释放快捷键  
        try:  
            msg = ctypes.wintypes.MSG()  

            while True:
                if user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:

                    if msg.message == win32con.WM_HOTKEY:  
                        if msg.wParam == id1:                               #激活热键
                            GO = True
                        elif msg.wParam == id2:
                            STOP = True
                        elif msg.wParam == id3:
                            EXIT = True

                    user32.TranslateMessage(ctypes.byref(msg))  
                    user32.DispatchMessageA(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, id1)                          #必须得释放热键，否则下次就会注册失败，所以当程序异常退出，没有释放热键，
                                                                        #那么下次很可能就没办法注册成功了，这时可以换一个热键测试
            user32.UnregisterHotKey(None, id2)

            user32.UnregisterHotKey(None, id3)

def monitor():                                                          #监视热键是否被激活
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

def closeWindow():                                                      #点击x是询问是否退出
    ans = tk.messagebox.askyesno(title='Warning',message='Close the application?',default='no')
    if ans:
        window.destroy()
    else:
        return

hotkey = Hotkey()                                                        #创建热键线程
hotkey.setDaemon(True)
hotkey.start()

T2 = threading.Thread(target=monitor)                                    #创建监听热键的线程
T2.setDaemon(True)
T2.start()

window.protocol('WM_DELETE_WINDOW', closeWindow)                        #接受到点击关闭时调用函数closeWindow

#以下为gui界面

window.title('password bruter')
window.geometry('500x330')                                              #设置分辨率
l = tk.Label(window, text="Brute every 'sleep' seconds from 'start' to 'end' which you set BELOW", font=('Arial', 11, 'bold'), width=100, height=2)
l.pack()                                                                #标题
m = tk.Label(window, text="Press 'F3' to quit the program! ! !", font=('Arial', 11, 'bold'), width=50, height=1, underline='8')
m.pack()  
stitle = tk.Label(window, text='start')
stitle.pack()
START = tk.Entry(window, cursor='plus', width=15)                     #start输入文本框
START.pack()
etitle = tk.Label(window, text='end')
etitle.pack()
END = tk.Entry(window, cursor='plus', width=15)                       #end输入文本框
END.pack()


b1 = tk.Button(window, text='ok', width=14, height=1, command=start_end)#按钮b1
b1.pack()
s = tk.Scale(window, label='select sleep interval', cursor='circle', sliderrelief='raised', sliderlength=50, tickinterval=0.2, bd=5, from_=0, to=1, resolution=0.001, orient=tk.HORIZONTAL, length=400, variable=SLEEP, command=interval)
s.pack()                                                                                        #设置sleep间隔滑块

          
b2 = tk.Button(window, text='start blasting(F1)', width=15, height=1, underline=16, command=brute)
b2.pack(side='left', anchor='w', padx=50)                                                        #按钮b2,开始爆破
b3 = tk.Button(window, text='stop blasting(F2)', width=15, height=1, underline=15, command=stop_thread)
b3.pack(side='right', anchor='e', padx=50)                                                      #按钮b3,停止进程

window.mainloop()