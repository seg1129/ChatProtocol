#!/usr/bin/python3

# Suzanne Gerace
# main client file

import socket
import time
import logging

logging.basicConfig(filename='client.log', level=logging.DEBUG)

# Functions to send user information ##########################################
def show_username_information():
    print("Please use one of the following hard-coded usernames:")
    print("Pamina, Dolce or George")
    print("Please enter username: ")

def show_password_information():
    print("\nPlease use hard coded value, 'ILovePittbulls' for the password")
    print("Please enter Password: ")

def show_process_command_state_info():
    print("Type 'send' to send a message to someone")
    print("Type 'receive' to receive messages")
    print("Type 'end' to stop this program")

# helper functions ############################################################
def send_username_to_server(username):
    message = 'USER' + username
    s.send(message.encode('utf-8'))

def send_password_to_server(password):
    password_command = 'PASS' + password
    s.send(password_command.encode('utf-8'))

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
    # TODO put this in a try/catch statement
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
        # if we receive a 500 then there was a problem with the server processing
        if (done_messages == '500'):
            print("error receiving messages")
            break
        message = server_response[4:].strip()
        s.send('250 received message'.encode('utf-8'))
        sender, message = message.split(':')
        print("Message from {0}: {1}".format(sender, message))

# Functions called directly in MAIN ###########################################
def process_username(username):
    username_succeed = False
    send_username_to_server(username)
    server_response = s.recv(1024).decode('ascii')
    # this means we are getting an error sending username to server
    if (str(server_response[:3]) == '560' or str(server_response[:3]) == '500'):
        while(username_succeed == False):
            print("\nThere was an issue sending your username to the server\n")
            show_username_information()
            send_username_to_server(str(input()))
            if (str(server_response[:3]) != '560'):
                username_succeed = True

def process_password(password):
    password_succeed = False
    send_password_to_server(password)
    # TODO process response and check for error code
    server_response = s.recv(1024).decode('ascii')[:3]
    if (str(server_response) == '565' or str(server_response) == '500'):
        while(password_succeed == False):
            print("\nThere was an issue validating your credentials\n")
            show_username_information()
            process_username(str(input()))
            show_password_information()
            send_password_to_server(str(input()))
            server_response = s.recv(1024).decode('ascii')[:3]
            if (server_response != '565' and str(server_response) != '500'):
                password_succeed = True

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
    show_username_information()
    process_username(str(input()))

    show_password_information()
    process_password(str(input()))

    show_process_command_state_info()
    user_input = str(input()).lower()
    if (user_input != 'end'):
        process_command(user_input)
        while True:
            show_process_command_state_info()
            user_input = str(input()).lower()
            if (user_input == 'end'):
                # TODO send TERM command
                break
            else:
                process_command(user_input)
    else:
        s.close()
