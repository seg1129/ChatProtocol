#!/usr/bin/python3

# Suzanne Gerace
# main client file

import socket
import time
# a socket object using IPv4
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local machine name
host = socket.gethostname()

port = 9990

# connection to hostname on the port.
s.connect(('localhost', port))

time.sleep(5)
print("connected to server")
# 1024 bytes is the maximum
msg = s.recv(1024)
time.sleep(5)
s.close()
print (msg.decode('ascii'))
