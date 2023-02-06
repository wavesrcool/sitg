import socket

target_host = "127.0.0.1"
target_port = 9990
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host.encode('utf-8'), target_port))
req = "GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
client.send(req.encode('utf-8'))
resp = client.recv(4096)
print(resp)
