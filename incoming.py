import re
import socket
import _mysql
import thread
import hashlib
from Queue import Queue
from socket_manager import socketManager
from message import fetchMessage, formatMessage

def newUser(request, clientSocket, socketMgr):
    db = _mysql.connect(host="localhost", user="root", passwd="root", db="IM")
    pieces = request.split(';')
    user = pieces[1]
    password = pieces[2]
    status = False

    # Create hash
    passhash = hashlib.sha224(password).hexdigest()

    query = """SELECT username FROM USERS
        WHERE username = '""" + re.escape(user) + """'"""
    db.query(query)
    result = db.store_result()
    if(len(result.fetch_row()) == 0):
        query = """INSERT INTO USERS (username,password,alias,active)
            VALUES (
                '""" + re.escape(user) + """',
                '""" + passhash + """',
                '""" + re.escape(user) + """',
                TRUE
                )"""
        db.query(query)
        query = """CREATE TABLE """ + re.escape(user) + """ (
                id bigint,
                username varchar(255) NOT NULL,
                accepted bool DEFAULT FALSE,
                FOREIGN KEY (id)
                    REFERENCES USERS(id)
                    ON DELETE CASCADE
            )"""
        db.query(query)

        # Add the client to the socket manager
        socketMgr.addSocket(clientSocket, user)
        print user + " created and added to socket manager"
        # 1 for true / it worked
        response = '\\status;1;\\newuser;' + user
        clientSocket.send(formatMessage(response))
    else:
        # 0 for false / user name taken
        response = '\\status;0;\\newuser;' + user
        clientSocket.send(formatMessage(response))

    db.close()

def manageIncoming(incomingQueue, socketMgr):
    # Create database connection
    db = _mysql.connect(host="localhost", user="root", passwd="root", db="IM")

    # Wipe any users who were left online if server went down
    db.query("""UPDATE USERS SET active = FALSE""")


    while True:
        # Block until queue gets an item
        clientSocket = incomingQueue.get()
        msgLength = clientSocket.recv(5)

        # Fetch the identifier + password from the client
        request = fetchMessage(int(msgLength), clientSocket)

        # Check if this is actually a request for a new user
        if(len(request) > 7 and request[:8] == '\\newuser'):
            thread.start_new_thread(newUser, (request, clientSocket, socketMgr))
            continue
        elif(len(request) < 8 or request[:8] != '\\connect'
            or request.isspace() or len(request.split(';')) != 3):
            # If the client is not talking properly, close him.
            text = '\\status;0;' + request
            clientSocket.send(formatMessage(text))
            clientSocket.close()
            continue

        pieces = request.split(';')

        # Collect user and password
        user = pieces[1]
        password = pieces[2]
        passhash = hashlib.sha224(password).hexdigest()

        # Verify user name and password
        query = """SELECT username FROM USERS
            WHERE username = '""" + re.escape(user) + """'
            AND password = '""" + passhash + """'"""
        db.query(query)
        result = db.store_result();
        if(len(result.fetch_row()) != 1):
            text = '\\status;0;\\connect;' + user
            clientSocket.send(formatMessage(text))
            continue

        # Add to socket manager and set active
        query = """UPDATE USERS SET active = TRUE
            WHERE username = '""" + re.escape(user) + """'"""
        db.query(query)
        text = '\\status;1;\\connect;' + user
        clientSocket.send(formatMessage(text))
        socketMgr.addSocket(clientSocket, user)
        print user + " added to socket manager"

