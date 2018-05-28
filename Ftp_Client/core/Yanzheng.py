from core import option
import json
def main():
    while True:
        client = option.FtpClient()
        client.cononect('localhost', 9999)
        print("-------welcome to ftp server system-------")
        username = input("enter your user name:")
        password = input("enter password:")
        info = {
            "action": 'test',
            "username": username,
            "password": str(password)
        }
        client.send(json.dumps(info).encode("utf-8"))  # 发送验证消息
        msg = client.recv()
        print(msg.decode())
        # 验证成功
        if msg.decode()=="True":
            print("登陆成功")
            client.interaction(username)
        else:
            print("密码或用户名错误.....重新输入")
            continue
