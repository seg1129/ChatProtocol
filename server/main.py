#!/usr/bin/python3
# Suzanne Gerace
# This is the server main file

import socket
import threading
import logging

log = logging.getLogger(__name__)


# using python thread libray to ensure protocol can handle multiple clients properly
class ChatServerProtocol(threading.Thread):
    def __init__(self, comm_socket, address):
        threading.Thread.__init__(self)
        # States
        self.idle = True
        self.user_validated = False
        self.authentication_validated = False
        self.process_command = False
        self.sending_message = False
        self.downloading_message = False
        self.error_processing = False
        # hard coded usernames and password
        self.usernames = ['Pamina', 'Dolce', 'George']
        self.password = 'ILovePittbulls'
        # client socket
        self.comm_socket = comm_socket
        self.address = address

    # overriding threading run fuction to process messages received from client
    def run(self):
        print("we made it to run")
        while True:
            print("we are in run")
            try:
                data = self.comm_socket.recv(1024).rstrip()
                print(data)
                try:
                    packet_from_client = data.decode('utf-8')
                except AttributeError:
                    packet_from_client = data
                log.debug('Received command', packet_from_client)
                if not packet_from_client:
                    break
            except socket.error as err:
                log.error('Receive error', err)

            try:
                # seperating the command and arguments passed in from the
                # client, see design PDU for message structure details
                cmd = packet_from_client[:4].strip().upper() or None
                arg = packet_from_client[4:].strip() or None

                # retreive function from class. if function does not exist
                # return a 500 error
                func = getattr(self, cmd)
                func(arg)
            except AttributeError as err:
                self.sendCommand('500 error.\r\n')
                log.error('Receive error', err)

    def USER(self, user):
        # TODO make this a try statement
        if not self.idle:
            # TODO add this error to the design document
            self.send_to_client('500 bad command.\r\n')
        elif not user:
            self.send_to_client('560 error receiving user.\r\n')
            log.error('error sending username')
        else:
            self.send_to_client('220 received username successfully.\r\n')
            log.error('received username successfully')
            self.user = user
            self.idle = False
            self.user_validated = True

    def PASS(self, password):
        if not self.user_validated:
            self.send_to_client('500 Bad command.\r\n')
        elif not password:
            self.send_to_client('565 error authenticating password')
            log.error('error receiving password')
        else:
            self.user_password = password
            if self.check_user_cred():
                self.send_to_client('230 user authenticated successfully')
                self.user_validated = False
                self.authentication_validated = True
            else:
                log.error('There was an issue with authentication')

    def check_user_cred(self):
        if (self.user_password == self.password and self.user in self.usernames):
            return True
        else:
            return False

    def send_to_client(self, message):
        self.comm_socket.send(message.encode('utf-8'))

if __name__ == "__main__":
    # a socket object using IPv4
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get local host name
    servHost = socket.gethostname()
    servPort = 5035
    print(servHost)
    # bind to the port
    server.bind(('localhost', servPort))

    server.listen()

    while True:
        # accept connection
        clientsocket, address = server.accept()
        client_socket = ChatServerProtocol(clientsocket, address)
        client_socket.start()
        print("Got a connection from %s" % str(address))

        msg = 'Sending a message to client \r\n'
        print("sent message to client")
        # client_socket.send_to_client(msg.encode('ascii'))
        client_socket.send_to_client(msg)
        # server.close()
