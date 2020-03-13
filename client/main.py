#!/usr/bin/python3

# Suzanne Gerace
# main client file
# TODO The top of each file should contain the class name, date, and purpose of the file.
# TODO:
'''Every function should have a comment block about it’s purpose and
   every file should have a comment block about who wrote the code and
   it’s purpose.
'''

import socket
import time
import logging

logging.basicConfig(filename='client.log', level=logging.DEBUG)

class chatProtocolClient:
    def __init__(self):
        self.idle = True
        self.user_validated = False
        self.authentication_validated = False
        self.process_command = False
        self.sending_message = False
        self.downloading_message = False
        self.error_processing = False

    # Functions to send user information ##########################################
    def show_username_information(self):
        print("Please use one of the following hard-coded usernames:")
        print("Pamina, Dolce or George")
        print("Please enter username: ")

    def show_password_information(self):
        print("\nPlease use hard coded value, 'ILovePittbulls' for the password")
        print("Please enter Password: ")

    def show_process_command_state_info(self):
        print("Type 'send' to send a message to someone")
        print("Type 'receive' to receive messages")
        print("Type 'end' to stop this program")

    # helper functions ############################################################
    def send_username_to_server(self, username):
        message = 'USER' + username
        s.send(message.encode('utf-8'))

    def send_password_to_server(self, password):
        password_command = 'PASS' + password
        s.send(password_command.encode('utf-8'))

    def send_message(self):
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

    def receive_messages(self):
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

    def end(self):
        print("close")
        message = 'TERM'
        s.send(message.encode('utf-8'))
        s.close()

    # Functions called directly in MAIN ###########################################
    def process_username(self, username):
        username_succeed = False
        self.send_username_to_server(username)
        server_response = s.recv(1024).decode('ascii')
        # this means we are getting an error sending username to server
        if (str(server_response[:3]) == '560' or str(server_response[:3]) == '500'):
            while(username_succeed == False):
                print("\nThere was an issue sending your username to the server\n")
                self.show_username_information()
                self.send_username_to_server(str(input()))
                if (str(server_response[:3]) != '560'):
                    username_succeed = True

    def process_password(self, password):
        password_succeed = False
        self.send_password_to_server(password)
        # TODO process response and check for error code
        server_response = s.recv(1024).decode('ascii')[:3]
        if (str(server_response) == '565' or str(server_response) == '500'):
            while(password_succeed == False):
                print("\nThere was an issue validating your credentials\n")
                self.show_username_information()
                self.process_username(str(input()))
                self.show_password_information()
                self.send_password_to_server(str(input()))
                server_response = s.recv(1024).decode('ascii')[:3]
                if (server_response != '565' and str(server_response) != '500'):
                    password_succeed = True

    def process_usr_command(self, command):
        if (command.lower() == 'send'):
            self.send_message()
        if (command.lower() == 'receive'):
            self.receive_messages()
        if (command.lower() == 'end'):
            print("close")
            s.close()

if __name__ == "__main__":
    # TODO pass in port and host as parameters

    # a socket object using IPv4
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get local machine name
    host = socket.gethostname()

    port = 5035
    # connection to hostname on the port.
    s.connect(('localhost', port))

    client = chatProtocolClient()

    print("Hello! welcome to Chat Protocol, we have successfully connected with the chat server.\n")
    client.show_username_information()
    client.process_username(str(input()))

    client.show_password_information()
    client.process_password(str(input()))

    client.show_process_command_state_info()
    user_input = str(input()).lower()
    if (user_input != 'end'):
        client.process_usr_command(user_input)
        while True:
            client.show_process_command_state_info()
            user_input = str(input()).lower()
            if (user_input == 'end'):
                # TODO send TERM command
                break
            else:
                client.process_usr_command(user_input)
    else:
        s.close()
