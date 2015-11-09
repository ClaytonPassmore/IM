import re
import rsa
import socket
import _mysql
import thread
import hashlib
from Queue import Queue
from socket_manager import socketManager
from message import fetchMessage, formatMessage, getMessageLengthString

def newUser(request, clientSocket, socketMgr, privateKey):
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
        print(user + ' created and added to socket manager')
        # 1 for true / it worked
        response = '\\status;1;\\newuser;' + user
        signature = rsa.sign(response, privateKey, 'SHA-1')
        clientSocket.send(formatMessage(response + ';' + signature))
    else:
        # 0 for false / user name taken
        response = '\\status;0;\\newuser;' + user
        signature = rsa.sign(response, privateKey, 'SHA-1')
        clientSocket.send(formatMessage(response + ';' + signature))

    db.close()

def manageIncoming(incomingQueue, socketMgr):
    # Read private key
    with open('keys/private.pem', 'r') as privateFile:
        keyData = privateFile.read()
    privateKey = rsa.PrivateKey.load_pkcs1(keyData, 'PEM')

    # Create database connection
    db = _mysql.connect(host="localhost", user="root", passwd="root", db="IM")

    # Wipe any users who were left online if server went down
    db.query("""UPDATE USERS SET active = FALSE""")


    while True:
        # Block until queue gets an item
        clientSocket = incomingQueue.get()
        msgLength = getMessageLengthString(clientSocket)
        if(len(msgLength) == 0):
            clientSocket.close()
            continue

        # Fetch the identifier + password from the client
        cipher = fetchMessage(int(msgLength), clientSocket)
        request = rsa.decrypt(cipher, privateKey)

        # Check if this is actually a request for a new user
        if(len(request) > 7 and request[:8] == '\\newuser'):
            thread.start_new_thread(newUser, (request, clientSocket, socketMgr, privateKey))
            continue
        elif(len(request) < 8 or request[:8] != '\\connect'
            or request.isspace() or len(request.split(';')) != 3):
            # If the client is not talking properly, close him.
            text = '\\status;0;' + request
            signature = rsa.sign(text, privateKey, 'SHA-1')
            clientSocket.send(formatMessage(text + ';' + signature))
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
            signature = rsa.sign(text, privateKey, 'SHA-1')
            clientSocket.send(formatMessage(text + ';' + signature))
            continue

        # Add to socket manager and set active
        query = """UPDATE USERS SET active = TRUE
            WHERE username = '""" + re.escape(user) + """'"""
        db.query(query)
        text = '\\status;1;\\connect;' + user
        signature = rsa.sign(text, privateKey, 'SHA-1')
        clientSocket.send(formatMessage(text + ';' + signature))
        socketMgr.addSocket(clientSocket, user)
        print(user + ' added to socket manager')

