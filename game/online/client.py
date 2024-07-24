# This file contains the code for multiplayer gameplay.
import socket

# 创建 TCP 套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 连接服务器
server_address = ('127.0.0.1', 5000)
client_socket.connect(server_address)

# 发送数据
data = "Hello from client!"
client_socket.send(data.encode('utf-8'))

# 接收服务器响应
response = client_socket.recv(1024)
print(f"Received from server: {response.decode('utf-8')}")

# 关闭连接
client_socket.close()