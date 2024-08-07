# 用于处理用户注册和登录功能
# Only able to register and login, and only saves username and password in a file.
# This file DO NOT save any game data.


import os
import sys


sys.path.append('../')  # 将父目录添加到系统路径
# 检查文件是否存在，如果不存在则创建
def file_initialize(file_path):
    if not os.path.exists(file_path):
        open(file_path, 'w').close()


# 注册功能
def register(username, password, file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            existing_username, _ = line.strip().split(',')
            if existing_username == username:
                print("用户名已存在，请重新输入！")
                return False
    with open(file_path, 'a') as f:
        f.write(f"{username},{password}\n")
    print("注册成功！")
    return True


# 登录功能
def login(username, password, file_path):
    with open(file_path, 'r') as f:
        for line in f.readlines():
            stored_username, stored_password = line.strip().split(',')
            if username == stored_username and password == stored_password:
                print("登录成功！")
                return True
    return False

