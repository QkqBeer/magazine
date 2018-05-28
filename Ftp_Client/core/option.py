import socket
import os
import json
import sys
class FtpClient(object):
    def __init__(self):
        self.current_dirpath = '' #指的是用户根目录之后的字符串，并不是真正的绝对路径
        self.client=socket.socket()
    def help(self,*args):
        mas='''
        ls
        cd
        get filename
        put filename
        '''
        print(mas)
 #连接
    def cononect(self,ip,port):
        self.client.connect((ip,port))
#交互
    def interaction(self,username):
        while True:
            cmd = input(">>:").strip()
            if len(cmd) == 0: continue
            cmd_str=cmd.split()[0]
            if hasattr(self,cmd_str):
                func=getattr(self,cmd_str )
                func(cmd,username)
    #上传文件
    def put(self,*args):
        cmd_split=args[0].split()
        if len(cmd_split)>1:
            filename=cmd_split[1]
            #确认文件是否存在
            if os.path.isfile(filename):
                filesize=os.stat(filename ).st_size
                msg_dic={
                    "action":'put',
                    "name":filename,
                    "size":filesize,
                    "username":args[1],
                    "overridden":True
                }
                #第一次传数据，将字典传过去
                self.client.send(json.dumps(msg_dic).encode("utf-8"))
                #防止黏包，等待服务器确认
                server_response=self.client.recv(1024)
                #打开文件，传输文件
                f=open(filename ,'rb')
                sent_size=0
                for line in f:
                    self.client.send(line)
                    sent_size+=len(line)
                    self.progress_bar(int(sent_size),filesize)
                else:
                    print("\nfile upload finished")
                    f.close()
            else:
                print("file %s not exist"%filename)
    #下载文件
    def get(self,*args):
        cmd_split = args[0].split()
        filename=cmd_split[1]
        if len(cmd_split) >1:
            cmd_dir={
                "action":'get',
                'name':filename
            }
            #第一次发送动作和文件名
            self.client.send(json.dumps(cmd_dir).encode("utf-8"))
            #收到文件是否存在和文件大小
            data=self.client.recv(1024)
            fileInf=json.loads(data.decode())

            if fileInf['isExist']:
                # 允许发送，防止黏包
                self.client.send(b"you can send data")
                f=open(filename,'wb')
                received_size=0
                while received_size <fileInf['size']:
                    filedata=self.client.recv(1024)
                    #写入文件
                    f.write(filedata)
                    received_size +=len(filedata)
                    self.progress_bar(int(received_size),int(fileInf['size']))
                else:
                    f.close()
                    print("\nload finished")
            else:
                print("file is not exist")
    #进度条
    def progress_bar(self,received_size,filesize):
            i=int(received_size//(filesize/20))
            s1 = "\r[%s%s]%d%%" %( "█" * i, " " * (20 - i),((i/20)*100))
            sys.stdout.write(s1)
            sys.stdout.flush()
    #发送
    def send(self,msg):
        self.client.send(msg)
    #接受
    def recv(self):
        return self.client.recv(1024)
    #改变工作目录
    def cd(self,*args):
        cmd_split = args[0].split()
        username=args[1]
        if len(cmd_split)>1:
            cmd_dir={
                'action':cmd_split[0],
                'updown':cmd_split[1],
                'username':username,
                'path':self.current_dirpath
                     }
            self.client.send(json.dumps(cmd_dir).encode("utf-8"))
            path=self.client.recv(1024)
            self.current_dirpath=json.loads(path.decode())
            print("当前工作目录：",self.current_dirpath)
    def listDir(self,*args):
        username=args[1]
        cmd_dir={
            'action':"listDir",
            'path':self.current_dirpath,
            'username':username
        }
        self.client.send(json.dumps(cmd_dir).encode("utf-8"))
        dir=self.client.recv(1024)
        print(json.loads(dir.decode()))





