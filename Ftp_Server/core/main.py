import socketserver
import json
import os
import sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
class MyTCPHandle(socketserver.BaseRequestHandler):
    #新建一个handle处理对象
    def handle(self):
        while True:
            try:
                #收到第一次数据，命令和其他数据
                self.data =self.request.recv(1024).strip()
                cmd_str=json.loads(self.data.decode())
                action=cmd_str['action']
                if hasattr(self,action):
                    func=getattr(self,action)
                    func(cmd_str)
                else:
                    print("输入异常")
            except ConnectionError as e:
                print("连接异常！！")
                break
    #用户上传
    def put(self,*args):
        cmd_str=args[0]
        filename=cmd_str['name']
        filesize=cmd_str['size']
        username=cmd_str['username']
        if os.path.exists(base_dir+"\\account\\"+username+"\\"+filename):
            f=open(base_dir+"\\account\\"+username+"\\"+filename+'.new','wb')
        else:
            f=open(base_dir+"\\account\\"+username+"\\"+filename,'wb')
        self.request.send(b'please send')
        received_size=0
        while received_size < filesize:
            data=self.request.recv(1024)
            f.write(data)
            received_size +=len(data)
        else:
            f.close()
            print("文件传输完毕！！！！")

#用户下载
    def get(self,*args):
        cmd_str=args[0]
        filename=cmd_str['name']
        if os.path.isfile(filename):
            filesize=os.stat(filename).st_size
            fileInf={
                'size':filesize,
                'isExist':True
            }
            #发送文件信息
            self.request.send(json.dumps(fileInf).encode("utf-8"))
            #防止数据黏包
            ok=self.request.recv(1024)
            #发送数据
            f=open(filename,'rb')
            for line in f:
                self.request.send(line)
            else:
                print("file upload finished")
                f.close()
        else:#文件不存在时
            fileInf = {
                'size': 0,
                'isExist': False
                      }
            self.request.send(json.dumps(fileInf).encode())
    def test(self,*args):
        cmd_str=args[0]
        username=cmd_str['username']
        password=cmd_str['password']
       # 判断文件是否存在
        if os.path.isfile(base_dir+"\\account\\"+"\\"+username+"\\"+username):
            f = open(base_dir+"\\account\\"+"\\"+username+"\\"+username, "rb")
            infdata = eval(f.read())
            if infdata['password'] == password:
                # 发送True
                self.request.send("True".encode("utf-8"))
            else:
                self.request.send("False".encode("utf-8"))
        else :
            #发送false
            self.request.send("False".encode("utf-8"))
    def cd(self,*args):
        cmd_dir=args[0]
        updown=cmd_dir['updown']
        path=cmd_dir['path']
        username=cmd_dir['username']
        #返回上一层
        if updown=='..':
            #if判断是否越界
            if path=="":
                self.request.send(json.dumps(username).encode("utf-8"))
            #越界时，接着返回当前路径（由于client写死了，没有做提示）
            else:
                # 没有越界时，返回上一层目录
                current_path=base_dir+"\\account\\"+path
                length=len(base_dir+"\\account")
                after_path=os.path.dirname(current_path)
                print(after_path[length+1:])
                self.request.send(json.dumps(after_path[length+1:]).encode("utf-8"))
        #向下深入一层
        else:
            #文件存在时，返回地址+\\updown
            if path=="":
                if os.path.exists(base_dir + "\\account\\" + username + "\\" + updown):
                    self.request.send(json.dumps(username + "\\" + updown).encode("utf-8"))
                # 文件不存在时,返回当前路径
                else:
                    self.request.send(json.dumps(username).encode("utf-8"))
            else:
                if os.path.exists(base_dir + "\\account\\" + path + "\\" + updown):
                    self.request.send(json.dumps(path + "\\" + updown).encode("utf-8"))
                # 文件不存在时,返回当前路径
                else:
                    self.request.send(json.dumps(path).encode("utf-8"))
    def listDir(self,*args):
        cmd_dir=args[0]
        current_path=cmd_dir['path']
        username=cmd_dir['username']
        if len(current_path)==0:
            #返回根工作目录 self.request.send()
            current_path=base_dir + "\\account\\" + username
        else:
            #返回current_path目录 self.request.send()
            current_path=base_dir + "\\account\\"+current_path
        list=os.listdir(current_path)
        self.request.send(json.dumps(list).encode("utf-8"))
def main():
    Host, Port = 'localhost', 9999
    server = socketserver.ThreadingTCPServer((Host, Port), MyTCPHandle)
    server.serve_forever()

