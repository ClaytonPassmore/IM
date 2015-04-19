import socket
import _mysql
import socket_manager
import re
from message import formatMessage

# Send a message to a contact
def sendMessage(request, s, ident, db, socketMgr):
    pieces = request.split(';')
    if(len(pieces) != 2):
        return
    recip = pieces[0]
    message = pieces[1]
    query = """
        SELECT username FROM """ + re.escape(ident) + """
        WHERE username = '""" + re.escape(recip) + """'
    """
    db.query(query)
    result = db.store_result()

    # Check if recip is a contact
    if(len(result.fetch_row()) == 0):
        text = '\\status;0;\\message;' + request
        s.send(formatMessage(text))
        return

    recipSocket = socketMgr.getSocket(recip)

    # Check if client is disconnected
    if(recipSocket == False):
        text = '\\status;0;\\message;' + request
        s.send(formatMessage(text))
        return

    # Send message to recip
    text = '\\message;' + ident + ';' + message
    msg = formatMessage(text)
    recipSocket.send(msg)

    # Send delivery confirmation to sender
    text = '\\status;1;\\message;' + recip
    s.send(formatMessage(text))

# Get client contact list
def getContacts(request, s, ident, db, socketMgr):
    query = """
        SELECT t1.username, t1.alias, t1.active
        FROM USERS AS t1
        INNER JOIN (
            SELECT username FROM """ + re.escape(ident) + """
            WHERE accepted = TRUE
        ) AS t2
        ON t1.username = t2.username
    """
    db.query(query)
    results = db.store_result()

    # Get all results
    results = results.fetch_row(0)

    # Send results to the client
    text = '\\contacts;' + str(results)
    msg = formatMessage(text)
    s.send(msg)

# Send a contact request
def addContact(request, s, ident, db, socketMgr):
    recip = request
    query = """
        SELECT id FROM USERS WHERE username = '""" + re.escape(recip) + """'
    """
    db.query(query)
    result = db.store_result()

    # Verify user exists
    rows = result.fetch_row()
    if(len(rows) == 0):
        text = '\\status;0;\\add;' + request
        s.send(formatMessage(text))
        return

    # Get recipient's unique ID
    recipID = rows[0][0]

    # See if recip has requested friendship
    query = """
        SELECT username FROM """ + re.escape(recip) + """
        WHERE username = '""" + re.escape(ident) + """'
    """
    db.query(query)
    result = db.store_result()

    accepted = "FALSE"
    if(len(result.fetch_row()) != 0):
        accepted = "TRUE"
        query = """
            UPDATE """ + re.escape(recip) + """ SET accepted = TRUE
            WHERE username = '""" + re.escape(ident) + """'
        """
        db.query(query)

    query = """
        INSERT INTO """ + re.escape(ident) + """ (id,username,accepted)
        VALUES (""" + recipID + """,'""" + re.escape(recip) + """',""" + accepted + """)
    """
    db.query(query)

    # Let client know that request was placed
    text = '\\status;1;\\add;' + request
    s.send(formatMessage(text))

# Set user's alias
def setAlias(request, s, ident, db, socketMgr):
    alias = request
    query = """UPDATE USERS SET alias = '""" + re.escape(alias) + """'
        WHERE username = '""" + re.escape(ident) + """'"""
    db.query(query)
    text = '\\status;1;\\alias;' + request
    s.send(formatMessage(text))

def work(socketMgr, jobQueue):

    # Create the database connection
    db = _mysql.connect(host="localhost", user="root", passwd="root", db="IM")

    while True:
        job = jobQueue.get()

        s = job['socket']
        ident = job['identifier']
        request = job['request']

        # Get the action that the client requests
        action = request.split(';')[0]
        content = request[(len(action)+1):]

        if(action == '\\message'):
            sendMessage(content, s, ident, db, socketMgr)
        elif(action == '\\contacts'):
            getContacts(content, s, ident, db, socketMgr)
        elif(action == '\\add'):
            addContact(content, s, ident, db, socketMgr)
        elif(action == '\\alias'):
            setAlias(content, s, ident, db, socketMgr)

