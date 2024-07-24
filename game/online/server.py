# This file is used to fetch the online game data from the server.

import socket

# 创建 TCP 套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 绑定地址和端口
server_address = ('127.0.0.1', 5000)
server_socket.bind(server_address)

# 监听连接
server_socket.listen(5)

# 等待客户端连接
client_socket, client_address = server_socket.accept()

# 接收客户端数据
data = client_socket.recv(1024)
print(f"Received from client: {data.decode('utf-8')}")

# 发送响应
response = "Hello from server!"
client_socket.send(response.encode('utf-8'))

# 关闭连接
client_socket.close()
server_socket.close()