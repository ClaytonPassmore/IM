import socket
from select import select
from message import fetchMessage
from socket_manager import socketManager

def clientListener(socketMgr):
    while True:
        if(len(socketMgr.getSockets()) == 0):
            continue
        socketList = select(socketMgr.getSockets(), [], [])
        for s in socketList[0]:
            ident = socketMgr.getLabel(s)
            msgLength = s.recv(5)

            # If socket is closed, remove it from the socket manager
            if(len(msgLength) == 0):
                socketMgr.removeSocket(s)
                print ident + " has let the chat."
                continue

            message = fetchMessage(int(msgLength), s)

            print ident + " says: " + message

