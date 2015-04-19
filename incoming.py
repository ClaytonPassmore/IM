import socket
from Queue import Queue
from socket_manager import socketManager
from message import fetchMessage

def manageIncoming(incomingQueue, socketMgr):
    while True:
        # Block until queue gets an item
        clientSocket = incomingQueue.get()
        msgLength = clientSocket.recv(5)

        # Fetch the identifier from the client
        # TODO verify with password
        identifier = fetchMessage(int(msgLength), clientSocket)

        # Add to socket manager
        socketMgr.addSocket(clientSocket, identifier)
        print identifier + " added to socket manager"

