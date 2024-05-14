import tkinter as tk
from tkinter import messagebox
import sys
import os

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)

# 获取当前文件的目录
current_directory = os.path.dirname(current_file_path)

# 获取上一级目录
parent_directory = os.path.dirname(current_directory)

# 将上一级目录添加到sys.path中，以便Python可以在那里查找模块
sys.path.append(parent_directory)

# 现在可以导入game目录下的user模块了
from game import user # 假设auth.py和game目录在同一父目录下
real_users = {}
current_username = None


def get_current_user():
    return current_username


def login_user(login_entry_username, login_entry_password):
    global real_users
    global current_username
    username = login_entry_username.get().strip()
    password = login_entry_password.get().strip()
    if username in real_users and real_users[username].name == username and real_users[username].password == password:
        messagebox.showinfo("Success", f"Login successful!, Welcome {username}")
        # 登录成功后，将current_user设置为登录的用户
        current_username = real_users[username]
        root.destroy()  # 关闭登录窗口
    else:
        messagebox.showerror("Error", "Invalid username or password.")


def register_user(register_window, register_entry_username, register_entry_password):
    username = register_entry_username.get()
    password = register_entry_password.get()  # 在真实应用中，密码应该被加密存储
    if username and password:
        # 创建User对象并存储到real_users字典中
        new_user = user.User(username, password,100000, 0)  # 假设新用户默认有1000现金和非管理员权限
        real_users[username] = new_user
        messagebox.showinfo("Success", "Registration successful!")
        register_window.destroy()  # 关闭注册窗口
    else:
        messagebox.showerror("Error", "Please fill in all fields.")
    # 注意：这里我们没有使用全局的current_user变量，因为我们可以直接操作real_users字典中的User对象。
    # 如果需要current_user变量，可以在登录成功后将其设置为real_users[username]。


def register():
    register_window = tk.Toplevel(root)
    register_window.title("Register")

    register_label_username = tk.Label(register_window, text="Username:")
    register_label_username.pack()
    register_entry_username = tk.Entry(register_window)
    register_entry_username.pack()

    register_label_password = tk.Label(register_window, text="Password:")
    register_label_password.pack()
    register_entry_password = tk.Entry(register_window, show='*')
    register_entry_password.pack()

    # 使用lambda将Entry控件传递给register_user函数
    register_button = tk.Button(register_window, text="Register",
                                command=lambda: register_user(register_window, register_entry_username,
                                                              register_entry_password))
    register_button.pack()


def start_auth_window():
    # 主窗口
    global root
    root = tk.Tk()
    root.title("Login")

    login_label_username = tk.Label(root, text="Username:")
    login_label_username.pack()
    login_entry_username = tk.Entry(root)
    login_entry_username.pack()

    login_label_password = tk.Label(root, text="Password:")
    login_label_password.pack()
    login_entry_password = tk.Entry(root, show='*')
    login_entry_password.pack()

    # 使用lambda将Entry控件传递给login_user函数
    login_button = tk.Button(root, text="Login",
                             command=lambda: login_user(login_entry_username, login_entry_password))
    login_button.pack()

    register_button = tk.Button(root, text="Register", command=register)
    register_button.pack()

    root.mainloop()