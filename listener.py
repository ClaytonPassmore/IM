import _mysql
import socket
from select import select
from message import fetchMessage
from socket_manager import socketManager

def disconnect(socket, identifier, db, socketMgr):
    socketMgr.removeSocket(socket)
    query = """UPDATE USERS SET active = FALSE WHERE username = '""" + identifier + """'"""
    db.query(query)
    print identifier + " has disconnected"

# Retrieve 5 bytes from the socket
def getMessageLengthString(socket):
    Total = 5
    soFar = 0
    length = ''
    while(soFar < Total):
        length += socket.recv(Total - soFar)
        soFar = len(length)
        if(soFar == 0):
            length = ''
            break;
    return length

# Listen on client ports and execute client requests
def clientListener(socketMgr):
    # Create the database connection
    db = _mysql.connect(host="localhost", user="root", passwd="root", db="IM")

    # Main loop
    while True:
        socketList = select(socketMgr.getSockets(), [], [], 1)
        for s in socketList[0]:
            ident = socketMgr.getLabel(s)
            msgLength = getMessageLengthString(s)

            # If socket is closed, remove it from the socket manager
            ident = socketMgr.getLabel(s)
            if(len(msgLength) == 0):
                disconnect(s, ident, db, socketMgr)
                continue

            request = fetchMessage(int(msgLength), s)

            print ident + " says: " + request

