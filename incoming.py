import socket
import _mysql
import thread
import hashlib
from Queue import Queue
from socket_manager import socketManager
from message import fetchMessage

def newUser(request, clientSocket, socketMgr):
    db = _mysql.connect(host="localhost", user="root", passwd="root", db="IM")
    user, password = request.split(';')[1:]
    status = False

    # Create hash
    passhash = hashlib.sha224(password).hexdigest()

    query = """SELECT username FROM USERS WHERE username = '""" + user + """'"""
    db.query(query)
    result = db.store_result()
    if(len(result.fetch_row()) == 0):
        query = """INSERT INTO USERS (username,password,active)
            VALUES ('""" + user + """','""" + passhash + """',TRUE)"""
        db.query(query)
        query = """CREATE TABLE """ + user + """ (
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
        clientSocket.send("1")
    else:
        # 0 for false / user name taken
        clientSocket.send("0")

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
        response = fetchMessage(int(msgLength), clientSocket)

        # Check if this is actually a request for a new user
        if(len(response) > 7 and response[:8] == '\\newuser'):
            thread.start_new_thread(newUser, (response, clientSocket, socketMgr))
            continue
        elif(len(response) < 8 or response[:8] != '\\connect' or response.isspace()):
            # If the client is not talking properly, close him.
            clientSocket.close()
            continue

        response = response.split(';')
        if(len(response) != 3):
            clientSocket.close()
            continue

        # Collect user and password
        user = response[1]
        password = response[2]
        passhash = hashlib.sha224(password).hexdigest()

        # Verify user name and password
        query = """SELECT username FROM USERS
            WHERE username = '""" + user + """'
            AND password = '""" + passhash + """'"""
        db.query(query)
        result = db.store_result();
        if(len(result.fetch_row()) != 1):
            continue

        # Add to socket manager and set active
        query = """UPDATE USERS SET active = TRUE
            WHERE username = '""" + user + """'"""
        db.query(query)
        socketMgr.addSocket(clientSocket, user)
        print user + " added to socket manager"

