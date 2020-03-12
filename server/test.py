#!/usr/bin/python3

# Suzanne Gerace
# test server file
# TODO The top of each file should contain the class name, date, and purpose of the file.
# TODO:
'''Every function should have a comment block about it’s purpose and
   every file should have a comment block about who wrote the code and
   it’s purpose.
'''

import socket
import time
import logging

logging.basicConfig(filename='server_test.log', level=logging.DEBUG)
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

rmsg_command = 'RMSG'
s.send(rmsg_command.encode('utf-8'))
rmsg_response = s.recv(1024)
print (rmsg_response.decode('ascii'))

smsg = 'SMSG Dolce:want to go to the doggy park Dolce?'
s.send(smsg.encode('utf-8'))
smsg_response = s.recv(1024)
print(smsg_response.decode('ascii'))

bad_password_command = 'PASSILovePittbulls'
s.send(bad_password_command.encode('utf-8'))
bad_pass_response = s.recv(1024)
print (bad_pass_response.decode('ascii'))
time.sleep(5)
s.close()
