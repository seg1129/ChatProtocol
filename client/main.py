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
    # TODO check Size of message make sure it does not go above 1024 plus receiver name
    data_to_send = 'SMSG' + receiver + ':' + message
    s.send(data_to_send.encode('utf-8'))
    # TODO process this response and check for error code
    server_response = s.recv(1024)
    print("your message has been sent\n")


def receive_messages():
    data_to_send = 'RMSG'
    s.send(data_to_send.encode('utf-8'))
    # show messages to the user untill there are no more messages
    while True:
        server_response = s.recv(1024).decode('ascii')
        done_messages = server_response[:4].strip() or None
        # if server sends 255 this means that there are no new messages
        if (done_messages == '255'):
            print("end of new messages\n")
            break
        # if server sends 256 this means the user has no new messages
        if (done_messages == '256'):
            print("No New Messages\n")
            break
        if (done_messages == '500'):
            print("error receiving messages")
            break
        message = server_response[4:].strip()
        s.send('250 received message'.encode('utf-8'))
        print(message)
        sender, message = message.split(':')
        print("message from {0}: {1}".format(sender, message))


def process_command(command):
    if (command.lower() == 'send'):
        send_message()
    if (command.lower() == 'receive'):
        receive_messages()
    if (command.lower() == 'end'):
        print("close")
        s.close()

if __name__ == "__main__":
    # a socket object using IPv4
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get local machine name
    host = socket.gethostname()

    port = 5035
    # connection to hostname on the port.
    s.connect(('localhost', port))


    print("Hello! welcome to Chat Protocol, we have successfully connected with the chat server.\n")
    print("Please use one of the following hard-coded usernames:")
    print("Pamina, Dolce or George")
    print("Please enter username: ")
    process_username(str(input()))
    print("\nPlease use hard coded value, 'ILovePittbulls' for the password")
    print("Please enter Password: ")
    process_password(str(input()))
    print("Type 'send' to send a message to someone")
    print("Type 'receive' to receive messages")
    print("Type 'end' to stop this program")
    user_input = str(input()).lower()
    if (user_input != 'end'):
        process_command(user_input)
        while True:
            print("Type 'send' to send a message to someone")
            print("Type 'receive' to receive messages")
            print("Type 'end' to stop this program")
            user_input = str(input()).lower()
            if (user_input == 'end'):
                # TODO send TERM command
                break
            else:
                process_command(user_input)
    else:
        s.close()
