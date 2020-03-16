#!/usr/bin/python3
# Suzanne Gerace
# 3/15/2020
'''
The purpose of this file is to send, receive, process commands to be performed
by the server of the chat protocol. Design elements of the server can be found
in the document entitled Updated_S_Gerace.pdf. The requirements can be found
in the document entitled Requirements_S_Gerace.PDF. Each requirement identified
in the requirements document that is implemented in this file will be labeled
in a comment starting with, 'Satisfying Requirement <requirement Number>' and
can be mapped back to specific requirement in requirements document.
'''

import socket
import threading
import logging
import sqlite3
from sqlite3 import Error

logging.basicConfig(filename='server.log', level=logging.DEBUG)

# using python thread libray to ensure protocol can handle multiple clients properly
# satisfying requirement 11.
class ChatServerProtocol(threading.Thread):
    def __init__(self, comm_socket, address):
        threading.Thread.__init__(self)
        # DFA Protocol States- Satisfying Requirement 1a
        self.idle = True
        self.user_validated = False
        self.authentication_validated = False
        self.process_command = False
        self.sending_message = False
        self.receiving_message = False
        self.error_processing = False
        # hard coded values
        self.usernames = ['Pamina', 'Dolce', 'George']
        self.password = 'ILovePittbulls'
        # client socket
        self.comm_socket = comm_socket
        self.address = address
        # database connection
        self.database = r"../chatProtocol.db"


    # overriding threading run fuction to process messages received from client
    def run(self):
        # add messages to database for testing
        self.add_test_messages_to_database()
        # when starting new thread set state to idle - Satisfying Requirement 1a
        self.change_state_to_idle()
        while True:
            try:
                data = self.comm_socket.recv(1024).rstrip()
                try:
                    packet_from_client = data.decode('utf-8')
                except AttributeError:
                    packet_from_client = data
                logging.info('Received command' + packet_from_client)
                if not packet_from_client:
                    break
            except socket.error as err:
                logging.error('Receive error' + str(err))

            try:
                # seperating the command and arguments passed in from the
                # client, see design PDU for message structure details
                cmd = packet_from_client[:4].strip().upper() or None
                arg = packet_from_client[4:].strip() or None
                if (str(cmd) == '200' or str(cmd) == '250'):
                    logging.info('client received message')
                else:
                    if (cmd == 'TERM'):
                        if (self.process_command or self.error_processing):
                            # Satisfying Requirement 1a
                            self.change_state_to_idle()
                            # removing thread when receiving TERM command from
                            # client. Satisfying requirement 7b.
                            break
                    # retreive function from class in a way that we can call it.
                    func = getattr(self, cmd)
                    func(arg)
            except AttributeError as err:
                # sending response code to client satisfying requirement 10a.
                self.send_to_client('500 error.\r\n')
                logging.error('Receive error' + str(err))

    # Function for server to receive and store username provided by client.
    # Satisfying requirement 4b
    def USER(self, user):
        try:
            # check state before performing any action-Satisfying Requirement 1b
            if not self.idle:
                # sending response code to client satisfying requirement 10a.
                self.send_to_client('500 bad command.\r\n')
            elif not user:
                # sending response code to client satisfying requirement 10a.
                self.send_to_client('560 error receiving user.\r\n')
                logging.error('error sending username')
            else:
                # sending response code to client satisfying requirement 10a.
                self.send_to_client('220 received username successfully.\r\n')
                logging.info('received username successfully')
                self.user = user
                # If successfully received user change state
                # Satisfying Requirement 1a
                self.change_state_to_user_validated()
        except:
            # sending response code to client satisfying requirement 10a.
            self.send_to_client('560 error receiving user.\r\n')
            logging.error('error sending username')

    # Function for server to receive and store password from client and validate
    # user credentials. Satisfying Requirement 4e.
    def PASS(self, password):
        try:
            # make sure state is at 'user_validated' before performing any action
            # Satisfying Requirement 1b
            if not self.user_validated:
                # send response to client Satisfying Requirement 4f
                # sending response code to client satisfying requirement 10a.
                self.send_to_client('500 Bad command.\r\n')
            elif not password:
                # send response to client Satisfying Requirement 4f
                # sending response code to client satisfying requirement 10a.
                self.send_to_client('565 error authenticating password')
                logging.error("error receiving password. user:{}".format(self.user))
                # if there is an error receivng password from client, change
                # state to idle. Satisfying Requirement 1a
                self.change_state_to_idle()
            else:
                # if password was received from client, change state to
                # 'authentication validated', Satisfying Requirement 1a
                self.change_state_to_auth_validated()
                self.user_password = password
                if self.check_user_cred():
                    print("credentials have been verified")
                    # send response to client Satisfying Requirement 4f
                    # sending response code to client satisfying requirement 10a.
                    self.send_to_client('230 user authenticated successfully')
                    self.change_state_to_process_command()
                else:
                    # if there is an error authenticating user, change
                    # state to idle. Satisfying Requirement 1a
                    self.change_state_to_idle()
                    # send response to client Satisfying Requirement 4f
                    # sending response code to client satisfying requirement 10a.
                    self.send_to_client('565 error authenticating password')
                    logging.error("There was an issue with authentication. user:{}".format(self.user))

        except:
            # if there is an error authenticating user, change
            # state to idle. Satisfying Requirement 1a
            self.change_state_to_idle()
            logging.error("There was an issue with authentication user:{}".format(self.user))
            # sending response code to client satisfying requirement 10a.
            self.send_to_client('565 error authenticating password')

    # This command will search for messages for a user and send them to the client
    # satisfying requirement 6b.
    def RMSG(self, usr_and_msg):
        try:
            # make sure state is at 'process_command' before performing any action
            # Satisfying Requirement 1b
            if (self.process_command != True):
                # sending response code to client satisfying requirement 10a.
                self.send_to_client('500 Bad command.\r\n')
                self.catch_201_from_client()
            else:
                # updating state to receiving messages. Satisfying Requirement 1a
                self.change_state_to_receiving_message()
                messages_query = self.get_messages_for_current_user()
                # if there are no mesages for the user - tell the client.
                # Satisfying requirement 6f.
                if (messages_query ==[]):
                    # sending response code to client satisfying requirement 10a.
                    self.send_to_client('256 no new messages')
                else:
                    # if new messages for given user is found in the database, send
                    # each message to the client one at a time. Satisfying
                    # Requirement 6c.
                    for m in messages_query:
                        # put query results into variables to be proccessed
                        sender = self.get_username(m[1])
                        message = m[2]
                        message_id = m[0]
                        # format of this data unit to client satisfying requirement 10b
                        message_to_client = "RMSG{}:{}".format(sender, message)
                        self.send_to_client(message_to_client)
                        client_response = self.comm_socket.recv(1024)
                        try:
                            self.remove_message_from_database(message_id)
                        except:
                            logging.error("error deleting message with id {}".format(message_id))
                    # sending response code to client satisfying requirement 10a.
                    self.send_to_client('255 end of messages')
                # once process is completed successfully, change state to process command
                # satisfying requirement 1a
                self.change_state_to_process_command()
        except:
            # sending response code to client satisfying requirement 10a.
            self.change_state_to_error_processing()
            self.send_client('550 error sending chat message to client')
            logging.error('error sending chat message to client')
            self.catch_201_from_client()

    def SMSG(self, usr_and_msg):
        try:
            # make sure state is at 'process_command' before performing any action
            # Satisfying Requirement 1b
            if (self.process_command != True):
                # sending response code to client satisfying requirement 10a.
                self.send_to_client('500 Bad command.\r\n')
                self.catch_201_from_client()
            else:
                # update state to 'sending message'. satisfying requirement 1a
                self.change_state_to_sending_msg()
                try:
                    # parsing data received from client satisfying requirement 5e
                    receiver, message = usr_and_msg.split(':')
                    # adds message, receiver and sender to database satisfying
                    # requirement 5f
                    sent_message_to_client = self.add_msg_to_database(receiver, message)
                    if (sent_message_to_client == False):
                        # send client response identifying status of request. satisfying
                        # requirement 5g
                        # sending response code to client satisfying requirement 10a.
                        self.send_to_client('200 message sent')
                except:
                    self.change_state_to_error_processing()
                    # sending response code to client satisfying requirement 10a.
                    self.send_to_client('546 too many : characters found in PDU from client')
                    logging.error('too many : characters found in PDU from client')
                    self.catch_201_from_client()

                # update to 'process command' when sending message action is
                # complete. Satisfying Requirement 1a
                self.change_state_to_process_command()
        except:
            self.change_state_to_error_processing()
            # sending response code to client satisfying requirement 10a.
            self.send_client('540 error sending chat message to client')
            logging.error('error sending chat message to client')
            self.catch_201_from_client()

    # wait for 201 from client to recover from 'error processing' state
    def catch_201_from_client(self):
        client_response = self.comm_socket.recv(1024).rstrip()
        if (client_response.decode('utf-8')[:3] == 201):
            self.change_state_to_process_command()

    # this function will add a message to the database and return True if sent
    # response back to client
    def add_msg_to_database(self, receiver, message):
        response_sent_to_client = False
        # make sure state is sending message before adding message to database
        # Satisfying Requrement 1b
        if (self.sending_message):
            sender = self.user
            sender_id = self.get_user_id(sender)
            receiver_id = self.get_user_id(receiver)
            if (receiver_id == None):
                self.change_state_to_error_processing()
                self.send_to_client('545 receiver user does not exist.\r\n')
                self.catch_201_from_client()
                response_sent_to_client = True
            else:
                try:
                    db_conn = self.connect_to_database(self.database)
                    cur = db_conn.cursor()
                    cur.execute("INSERT INTO messages VALUES (?,?,?)", (sender_id, receiver_id, message))
                    db_conn.commit()
                    db_conn.close()
                    response_sent_to_client = False
                except Error as e:
                    print(e)
                    logging.error("error adding message to database. message:{}, user: {}".format(message, sender))
                    self.change_state_to_error_processing()
                    # sending response code to client satisfying requirement 10a.
                    self.send_client('540 error sending chat message to client')
                    logging.error('error sending chat message to client')
                    self.catch_201_from_client()
                    response_sent_to_client = True
        else:
            # sending response code to client satisfying requirement 10a.
            self.send_to_client('500 Bad command.\r\n')
            self.catch_201_from_client()
            response_sent_to_client = True
        return response_sent_to_client

    def check_user_cred(self):
        if (self.user_password == self.password and self.user in self.usernames):
            return True
        else:
            return False

    def send_to_client(self, message):
        self.comm_socket.send(message.encode('utf-8'))

    def connect_to_database(self, db):
        db_conn = None
        try:
            db_conn = sqlite3.connect(db)
        except Error as e:
            print(e)
        return db_conn

    def get_user_id(self, user):
        db_conn = self.connect_to_database(self.database)
        cur = db_conn.cursor()
        cur.execute("SELECT rowid FROM user WHERE user=?", (user,))
        user_id = cur.fetchone() or None
        db_conn.close()
        if (user_id == None):
            return None
        else:
            return user_id[0]

    def get_username(self, user_id):
        # make sure state is 'receiving messages' before getting username from
        # database. Satisfying Requirement 1b
        if self.receiving_message:
            db_conn = self.connect_to_database(self.database)
            cur = db_conn.cursor()
            cur.execute("SELECT user FROM user WHERE rowid=?", (user_id,))
            username = cur.fetchone()
            db_conn.close()
            return username[0]
        else:
            # if there is an issue getting username from database, update state
            # to error_processing. Satisfying Requirement 1a
            self.change_state_to_error_processing()

    def get_messages_for_current_user(self):
        if self.receiving_message:
            user_id = self.get_user_id(self.user)
            db_conn = self.connect_to_database(self.database)
            cur = db_conn.cursor()
            cur.execute("SELECT rowid, sender, message FROM messages WHERE receiver=?", (user_id,))
            messages = cur.fetchall()
            db_conn.close()
            return messages
        else:
            # if there is an issue getting messages from database, update state
            # to error_processing. Satisfying Requirement 1a
            self.change_state_to_error_processing()

    def remove_message_from_database(self, message_id):
        # check state before connecting to database to remove messages
        if self.receiving_message:
            db_conn = self.connect_to_database(self.database)
            cur = db_conn.cursor()
            cur.execute("delete from messages where rowid=?", (message_id,))
            db_conn.commit()
            db_conn.close()
        else:
            # if there is an issue deleting messages from database, update state
            # to error_processing. Satisfying Requirement 1a
            self.change_state_to_error_processing()

    def add_test_messages_to_database(self):
        db_conn = self.connect_to_database(self.database)
        cur = db_conn.cursor()
        cur.execute("INSERT INTO messages VALUES(1,2,'Hi George!')")
        cur.execute("INSERT INTO messages VALUES(2,1,'Hi Pamina')")
        cur.execute("INSERT INTO messages VALUES(3,1,'Hello Pamina! How are you?')")
        cur.execute("INSERT INTO messages VALUES(1,3,'I am good! how about you?')")
        db_conn.commit()
        db_conn.close()

    # change of state functions ###############################################
    # Satisfying Requirement 1a
    def change_state_to_idle(self):
        self.idle = True
        self.user_validated = False
        self.authentication_validated = False
        self.process_command = False
        self.sending_message = False
        self.receiving_message = False
        self.error_processing = False

    # Satisfying Requirement 1a
    def change_state_to_user_validated(self):
        self.idle = False
        self.user_validated = True
        self.authentication_validated = False
        self.process_command = False
        self.sending_message = False
        self.receiving_message = False
        self.error_processing = False

    # Satisfying Requirement 1a
    def change_state_to_auth_validated(self):
        self.idle = False
        self.user_validated = False
        self.authentication_validated = True
        self.process_command = False
        self.sending_message = False
        self.receiving_message = False
        self.error_processing = False

    # Satisfying Requirement 1a
    def change_state_to_process_command(self):
        self.idle = False
        self.user_validated = False
        self.authentication_validated = False
        self.process_command = True
        self.sending_message = False
        self.receiving_message = False
        self.error_processing = False

    # Satisfying Requirement 1a
    def change_state_to_sending_msg(self):
        self.idle = False
        self.user_validated = False
        self.authentication_validated = False
        self.process_command = False
        self.sending_message = True
        self.receiving_message = False
        self.error_processing = False

    # Satisfying Requirement 1a
    def change_state_to_receiving_message(self):
        self.idle = False
        self.user_validated = False
        self.authentication_validated = False
        self.process_command = False
        self.sending_message = False
        self.receiving_message = True
        self.error_processing = False

    # Satisfying Requirement 1a
    def change_state_to_error_processing(self):
        self.idle = False
        self.user_validated = False
        self.authentication_validated = False
        self.process_command = False
        self.sending_message = False
        self.receiving_message = False
        self.error_processing = True

# main function to initalize server program. Satisfying Requirement 2
if __name__ == "__main__":

    # a socket object using IPv4 (AF_INET)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    servPort = 5035
    server_host = socket.gethostname()
    print(server_host)
    # bind to the port
    server.bind((server_host, servPort))

    server.listen()

    while True:
        # accept connection
        clientsocket, address = server.accept()
        client_socket = ChatServerProtocol(clientsocket, address)
        client_socket.start()
        print("Got a connection from %s" % str(address))
