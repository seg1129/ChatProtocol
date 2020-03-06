#!/usr/bin/python3

# Suzanne Gerace
# main client file

import socket
import time
import logging

logging.basicConfig(filename='client.log', level=logging.DEBUG)
# a socket object using IPv4
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local machine name
host = socket.gethostname()

port = 5035

# connection to hostname on the port.
s.connect(('localhost', port))

time.sleep(5)
print("connected to server")
# 1024 bytes is the maximum
msg = s.recv(1024)
print (msg.decode('ascii'))
# send username
message = 'USERPamina'
s.send(message.encode('utf-8'))
msg2 = s.recv(1024)
print (msg2.decode('ascii'))
time.sleep(5)
# send password
password_command = 'PASSILovePittbulls'
s.send(password_command.encode('utf-8'))
pass_response = s.recv(1024)
print (pass_response.decode('ascii'))

bad_password_command = 'PASSILovePittbulls'
s.send(bad_password_command.encode('utf-8'))
bad_pass_response = s.recv(1024)
print (bad_pass_response.decode('ascii'))
time.sleep(5)
s.close()
