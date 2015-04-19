import re
import _mysql
import socket
from Queue import Queue
from select import select
from message import fetchMessage, getMessageLengthString
from socket_manager import socketManager

def disconnect(socket, identifier, db, socketMgr):
    socketMgr.removeSocket(socket)
    query = """UPDATE USERS SET active = FALSE 
    WHERE username = '""" + re.escape(identifier) + """'"""
    db.query(query)
    print identifier + " has disconnected"

# Listen on client ports and execute client requests
def clientListener(socketMgr, jobQueue):
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

            # Fetch the entire message
            request = fetchMessage(int(msgLength), s)

            # Put info in the job queue
            item = {
                'identifier': ident,
                'socket': s,
                'request': request
            }
            jobQueue.put(item)

