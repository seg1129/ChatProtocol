#!/usr/bin/python3           # This is server.py file
import socket
import selectors
import threading
#
sel = selectors.DefaultSelector()
# a socket object using IPv4
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local host name
servHost = socket.gethostname()
servPort = 9090
print(servHost)
# bind to the port
server.bind(('localhost', servPort))

server.listen()
# using this to keep from blocking port allowing multiple requests to this client
# server.setblocking(False)
while True:
    # accept connection
    clientsocket, addr = server.accept()
    clientsocket.setblocking(False)

    print("Got a connection from %s" % str(addr))

    msg = 'Sending a message to client'+ "\r\n"
    print("sent message to client")
    clientsocket.send(msg.encode('ascii'))
    clientsocket.close()
