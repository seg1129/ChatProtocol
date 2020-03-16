#!/usr/bin/python3

# Suzanne Gerace
# test server file. This file is used to test the server


import socket
import time
import logging


def process_response_rmsg( response_code):
    break_loop = False
    # if server sends 255 this means that there are no new messages
    if (response_code == '255'):
        print("end of new messages\n")
        break_loop = True
    # if server sends 256 this means the user has no new messages
    elif (response_code == '256'):
        print("No New Messages\n")
        break_loop = True
    # if we receive a 500 then there was a problem with the server processing
    elif (response_code == '500'):
        print("error receiving messages")
        break_loop = True
    return break_loop


logging.basicConfig(filename='server_test.log', level=logging.DEBUG)
if __name__ == "__main__":
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
    # msg = s.recv(1024)
    # print (msg.decode('ascii'))
    # send username
    message = 'USERPamina'
    s.send(message.encode('utf-8'))
    msg2 = s.recv(1024)
    print (msg2.decode('ascii'))
    # time.sleep(5)
    # send password
    password_command = 'PASSILovePittbulls'
    s.send(password_command.encode('utf-8'))
    pass_response = s.recv(1024)
    print (pass_response.decode('ascii'))

    print("RMSG")
    rmsg_command = 'RMSG'
    s.send(rmsg_command.encode('utf-8'))
    while True:
        server_response = s.recv(1024).decode('ascii')
        server_response_code = server_response[:3].strip() or None

        # display to user response from server, satisfying requirement
        # 6g.
        break_loop = process_response_rmsg(server_response_code)
        if (break_loop):
            break
        message = server_response[4:].strip()
        # this response code to server satifies PDU requirment 9e.
        s.send('250 received message'.encode('utf-8'))
        sender, message = message.split(':')
        print("Message from {0}: {1}".format(sender, message))
    # rmsg_response = s.recv(1024)
    # print (rmsg_response.decode('ascii'))

    print("smsg")
    smsg = 'SMSG Dolce:want to go to the doggy park Dolce?'
    s.send(smsg.encode('utf-8'))
    smsg_response = s.recv(1024)
    print(smsg_response.decode('ascii'))

    print("out of order command")
    bad_password_command = 'PASSILovePittbulls'
    s.send(bad_password_command.encode('utf-8'))
    bad_pass_response = s.recv(1024)
    print (bad_pass_response.decode('ascii'))
    # time.sleep(5)

    print("command that DNE")
    bad_command_DNE = 'DNE'
    s.send(bad_command_DNE.encode('utf-8'))
    bad_command_DNE_response = s.recv(1024)
    print(bad_command_DNE_response.decode('ascii'))
    s.close()
