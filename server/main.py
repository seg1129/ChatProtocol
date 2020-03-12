#!/usr/bin/python3
# Suzanne Gerace
# This is the server main file
# TODO: The top of each file should contain the class name, date, and purpose of the file.
# TODO:
'''Every function should have a comment block about it’s purpose and
   every file should have a comment block about who wrote the code and
   it’s purpose.
'''
import socket
import threading
import logging
import sqlite3
from sqlite3 import Error

logging.basicConfig(filename='server.log', level=logging.DEBUG)

# using python thread libray to ensure protocol can handle multiple clients properly
class ChatServerProtocol(threading.Thread):
    def __init__(self, comm_socket, address):
        threading.Thread.__init__(self)
        # DFA Protocol States
        self.idle = True
        self.user_validated = False
        self.authentication_validated = False
        self.process_command = False
        self.sending_message = False
        self.downloading_message = False
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
                    # retreive function from class in a way that we can call it.
                    func = getattr(self, cmd)
                    func(arg)
            except AttributeError as err:
                self.send_to_client('500 error.\r\n')
                logging.error('Receive error' + str(err))

    def USER(self, user):
        try:
            if not self.idle:
                # TODO add this error to the design document
                self.send_to_client('500 bad command.\r\n')
            elif not user:
                self.send_to_client('560 error receiving user.\r\n')
                logging.error('error sending username')
            else:
                self.send_to_client('220 received username successfully.\r\n')
                logging.info('received username successfully')
                self.user = user
                self.idle = False
                self.user_validated = True
        except:
            self.send_to_client('560 error receiving user.\r\n')
            logging.error('error sending username')

    def PASS(self, password):
        # self.user_validated = False
        # TODO rethink this state

        try:
            if not self.user_validated:
                self.send_to_client('500 Bad command.\r\n')
            elif not password:
                self.send_to_client('565 error authenticating password')
                logging.error("error receiving password. user:{}".format(self.user))
                self.user_validated = False
                self.idle = True
            else:
                self.authentication_validated = True
                self.user_password = password
                if self.check_user_cred():
                    print("credentials have been verified")
                    self.send_to_client('230 user authenticated successfully')
                    self.authentication_validated = False
                    self.process_command = True

                else:
                    self.idle = True
                    self.send_to_client('565 error authenticating password')
                    logging.error("There was an issue with authentication. user:{}".format(self.user))

        except:
            logging.error("There was an issue with authentication user:{}".format(self.user))
            self.send_to_client('565 error authenticating password')

    # This command will search for messages for a user and send them to the client
    def RMSG(self, usr_and_msg):

        try:
            if not self.process_command:
                self.send_to_client('500 Bad command.\r\n')

            else:
                messages_query = self.get_messages_for_current_user()
                # if there are no mesages for the user - tell the client.
                if (messages_query ==[]):
                    self.send_to_client('256 no new messages')
                for m in messages_query:
                    # put query results into variables to be proccessed
                    sender = self.get_username(m[1])
                    message = m[2]
                    message_id = m[0]
                    # TODO if there are more than one : catch this error
                    message_to_client = "SMSG{}:{}".format(sender, message)
                    self.send_to_client(message_to_client)
                    client_response = self.comm_socket.recv(1024)
                    # TODO process response - if success - delete message from db

                    try:
                        self.remove_message_from_database(message_id)
                    except:
                        logging.error("error deleting message with id {}".format(message_id))
                self.send_to_client('255 end of messages')
            # TODO send back command response codes - do i need to do this?
        except:
            self.send_client('550 error sending chat message to client')
            logging.error('error sending chat message to client')

    def SMSG(self, usr_and_msg):
        # TODO what state should we be in when message has been received and what
        # should the state become?
        # TODO add a try catch statement
        receiver, message = usr_and_msg.split(':')
        # TODO check to make sure that message from client does not have ":" in it.
        self.add_msg_to_database(receiver, message)
        # TODO send back command response codes
        self.send_to_client('200 message sent')

    # TODO add TERM command here

    def add_msg_to_database(self, receiver, message):
        sender = self.user
        sender_id = self.get_user_id(sender)
        receiver_id = self.get_user_id(receiver)
        try:
            db_conn = self.connect_to_database(self.database)
            cur = db_conn.cursor()
            cur.execute("INSERT INTO messages VALUES (?,?,?)", (sender_id, receiver_id, message))
            db_conn.commit()
            db_conn.close()
            return True
        except Error as e:
            print(e)
            logging.error("error adding message to database. message:{}, user: {}".format(message, sender))
            return False
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
        # cur.execute(".tables")
        user_id = cur.fetchone()
        # print (user_id[0])
        db_conn.close()
        return user_id[0]

    def get_username(self, user_id):
        db_conn = self.connect_to_database(self.database)
        cur = db_conn.cursor()
        cur.execute("SELECT user FROM user WHERE rowid=?", (user_id,))

        username = cur.fetchone()
        print (username[0])
        db_conn.close()
        return username[0]

    def get_messages_for_current_user(self):
        # user_id = int(str(self.get_current_user_id()))
        user_id = self.get_user_id(self.user)
        db_conn = self.connect_to_database(self.database)
        cur = db_conn.cursor()
        cur.execute("SELECT rowid, sender, message FROM messages WHERE receiver=?", (user_id,))
        messages = cur.fetchall()
        # for row in rows:
        #     print (row)
        db_conn.close()
        return messages

    def remove_message_from_database(self, message_id):
        db_conn = self.connect_to_database(self.database)
        cur = db_conn.cursor()
        cur.execute("delete from messages where rowid=?", (message_id,))
        db_conn.commit()
        db_conn.close()


    def add_test_messages_to_database(self):
        db_conn = self.connect_to_database(self.database)
        cur = db_conn.cursor()
        cur.execute("INSERT INTO messages VALUES(1,2,'Hi George!')")
        cur.execute("INSERT INTO messages VALUES(2,1,'Hi Pamina')")
        cur.execute("INSERT INTO messages VALUES(3,1,'Hello Pamina! How are you?')")
        cur.execute("INSERT INTO messages VALUES(1,3,'I am good! how about you?')")
        db_conn.commit()
        db_conn.close()


if __name__ == "__main__":

    # a socket object using IPv4 (AF_INET)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #db_conn = connect_to_database(database)
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
