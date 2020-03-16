#!/usr/bin/python3

# Suzanne Gerace
# 3/15/2020
'''
The purpose of this file is to send, receive, process commands to be performed
by the client of the chat protocol. Design elements of the client can be found
in the document entitled Updated_S_Gerace.pdf. The requirements can be found
in the document entitled Requirements_S_Gerace.PDF. Each requirement identified
in the requirements document that is implemented in this file will be labeled
in a comment starting with, 'Satisfying Requirement <requirement Number>' and
can be mapped back to specific requirement in requirements document.
'''
# TODO:
'''Every function should have a comment block about it’s purpose and
   every file should have a comment block about who wrote the code and
   it’s purpose.
'''

import socket
import time
import logging
import sys

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
    # Functions in this section satisfy requirement 8b.

    # Client user interface to ask user for username satisfying requirements 4a and 8c
    def show_username_information(self):
        print("Please use one of the following hard-coded usernames:")
        print("Pamina, Dolce or George")
        print("Please enter username: ")

    # Client user interface to ask user for password satisfying requriement 4c and 8c
    def show_password_information(self):
        print("\nPlease use hard coded value, 'ILovePittbulls' for the password")
        print("Please enter Password: ")

    def show_process_command_state_info(self):
        print("Type 'send' to send a message to someone")
        print("Type 'receive' to receive messages")
        print("Type 'end' to stop this program")

    # helper functions ############################################################

    # If server indicates that there is an error in getting messages or there
    # are no more messages for user, return boolean variable to idicate if loop
    # should end. Notify user of reponse from server satisfying requirement 6g
    def process_response_rmsg(self, response_code):
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

    def process_response_smsg(self, server_response):
        server_response_code = str(server_response[:3].strip())
        print(server_response_code)
        if (server_response_code == '500'):
            print("bad command\n")
        elif(server_response_code == '555'):
            print(": found in message, this is an error\n")
        elif(server_response_code == '550'):
            print("server had error sending message\n")
        elif(server_response_code == '545'):
            print("user selected to receive message does not exist\n")
        else:
            print("your message has been sent\n")

    # PDU requirement for USER command, satisfying requirement 9a.
    def send_username_to_server(self, username):
        message = 'USER' + username
        s.send(message.encode('utf-8'))

    # PDU requirement for PASS command, satisfying requirement 9b
    def send_password_to_server(self, password):
        password_command = 'PASS' + password
        s.send(password_command.encode('utf-8'))

    def process_user_input_message(self, message):
        # check if user included ':' in message, if so do not continue with process
        if (':' in message):
            print(" : was included in your message and cannot be sent.")
            self.error_processing = True
        # check if user message is too long, if so do not continue with process
        if (len(message) > 1009):
            print("message was over 1009 characters and cannot be sent")
            self.error_processing = True

    # send message and receiver to server, satisfying requirement 5d.
    def send_new_message_to_server(self, receiver, message):
        # PDU satisfies requirement 9c.
        data_to_send = 'SMSG' + receiver + ':' + message
        s.send(data_to_send.encode('utf-8'))

    def send_message(self):
        error = False
        # when user wants to send a message to another user, first ask who they
        # would like to send a message to, satisfying requirement 5a.
        print("Who would you like to send a message to? ")
        receiver = str(input())

        # get message from user satisfying requirement 5b. Tell user message
        # cannot exceed 1009 characters, satisfying requirement 5c.
        print("Do not include ':' character in your message, and keep your message under 1009 characters. Type your message: ")
        message = str(input())
        self.process_user_input_message(message)

        if (self.error_processing == False):
            self.send_new_message_to_server(receiver, message)
            server_response = s.recv(1024).decode('ascii')

            # notify user of request status from the server, satisfying requirement 5h
            self.process_response_smsg(server_response)

        else:
            self.error_processing = False

    def receive_messages(self):
        try:
            # Send command to server to receive new messages, Satisfying
            # requirement 6a. PDU satisfies requirement 9d.
            data_to_send = 'RMSG'
            s.send(data_to_send.encode('utf-8'))
            # show messages to the user untill there are no more messages,
            # satisfying requirements 6e.
            while True:
                server_response = s.recv(1024).decode('ascii')
                server_response_code = server_response[:3].strip() or None

                # display to user response from server, satisfying requirement
                # 6g.
                break_loop = self.process_response_rmsg(server_response_code)
                if (break_loop):
                    break
                message = server_response[4:].strip()
                # this response code to server satifies PDU requirment 9e.
                s.send('250 received message'.encode('utf-8'))
                sender, message = message.split(':')
                print("Message from {0}: {1}".format(sender, message))
        except:
            print("error receiving messages")

    def end(self):
        print("close")
        # The PDU for this command satisfies requirement 9f.
        message = 'TERM'
        s.send(message.encode('utf-8'))
        s.close()

    # Functions called directly in MAIN ###########################################

    def process_username(self, username):
        username_succeed = False
        # take username from user and send to server satisfying requirement 4a.
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
        # take password from user and send to server satisfying requirement 4d
        self.send_password_to_server(password)
        server_response = s.recv(1024).decode('ascii')[:3]
        # process response and check for error code
        if (str(server_response) == '565' or str(server_response) == '500'):
            # if there was an error validating user, keep repeating process untill
            # successfully validated. Satisfying requirement 4g.
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
    # get hostname of server from commandline first parameter, Satisfying
    # requirement 3a.
    server_host = sys.argv[1] or None
    # a socket object using IPv4
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if (server_host == None):
        # get local machine name
        server_host = socket.gethostname()

    port = 5035
    # connection to server satisfying requirement 3b.
    s.connect((server_host, port))

    client = chatProtocolClient()

    print("Hello! welcome to Chat Protocol, we have successfully connected with the chat server.\n")
    client.show_username_information()
    client.process_username(str(input()))

    client.show_password_information()
    client.process_password(str(input()))

    # Once username and password have been verified, give user instructions
    # on what commands are not available to them. Satisfying requirement 8a.
    client.show_process_command_state_info()
    user_input = str(input()).lower()
    if (user_input != 'end'):
        client.process_usr_command(user_input)
        while True:
            client.show_process_command_state_info()
            user_input = str(input()).lower()

            if (user_input == 'end'):
                # when user sends request to end the client, send a command to
                # server terminate current thread in server.
                # Satisfying requirement 7a.
                client.end()
                # when user sends request to end the client, end client program
                # Satisfying requirement 7c.
                break
            else:
                client.process_usr_command(user_input)
    else:
        s.close()
