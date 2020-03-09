#!/usr/bin/python3

# Suzanne Gerace
# main client file

import socket
import time
import logging

logging.basicConfig(filename='client.log', level=logging.DEBUG)

def process_username(username):
    user_response = None
    message = 'USER' + username
    s.send(message.encode('utf-8'))
    while (user_response == None):
        user_response = s.recv(1024) or None
    #     print("user_response")
    #     print(user_response)
    # print("client response:")
    # print (user_response.decode('ascii'))
    # print("successfull processed username")

def process_password(password):
    password_command = 'PASS' + password
    s.send(password_command.encode('utf-8'))
    # TODO process response and check for error code
    server_response = s.recv(1024)

def send_message():
    print("Who would you like to send a message to? ")
    receiver = str(input())
    print("Do not include ':' character in your message. Type your message: ")
    message = str(input())
    # TODO remove any ':' in message
    data_to_send = 'SMSG' + receiver + ':' + message
    s.send(data_to_send.encode('utf-8'))
    # TODO process this response and check for error code
    server_response = s.recv(1024)


def receive_messages():
    data_to_send = 'RMSG'
    s.send(data_to_send.encode('utf-8'))
    # print messages to the user untill there are no more messages
    while True:
        server_response = s.recv(1024).decode('ascii')
        done_messages = server_response[:4].strip() or None
        # if done_messages is 205 this means there are no more messages
        if (done_messages == '255'):
            break
        message = server_response[4:].strip()
        s.send('250 received message'.encode('utf-8'))
        sender, message = message.split(':')
        print("message from {0}: {1}".format(sender, message))

def process_command(command):
    if (command.lower() == 'send'):
        send_message()
    if (command.lower() == 'receive'):
        receive_messages()

if __name__ == "__main__":
    # a socket object using IPv4
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get local machine name
    host = socket.gethostname()

    port = 5035
    # connection to hostname on the port.
    s.connect(('localhost', port))


    print("Hello! welcome to Chat Protocol, we have successfully connected with the chat server.\n")
    print(" Please use one of the following hard-coded usernames:\n")
    print("Pamina, Dolce or George\n")
    print("Please enter username: ")
    process_username(str(input()))
    print("Please use hard coded value, 'ILovePittbulls' for the password\n")
    print("Please enter Password: ")
    process_password(str(input()))
    print("Type 'send' to send a message to someone")
    print("Type 'receive' to receive messages")
    process_command(str(input()))
    while True:
        print("Type 'send' to send a message to someone")
        print("Type 'receive' to receive messages")
        process_command(str(input()))
    s.close()
