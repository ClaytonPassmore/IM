import socket

# Fetch 'length' bytes from 'clientSocket'
def fetchMessage(length, clientSocket):
    lengthSoFar = 0;
    message = ''
    while(lengthSoFar < length):
        partial = clientSocket.recv(length - lengthSoFar)
        if(len(partial) == 0):
            return ''
        message += partial
        lengthSoFar += len(partial)

    return message

def formatMessage(text):
    length = len(text)
    return ('%05d' % length) + text

# Retrieve 5 bytes from the socket
def getMessageLengthString(s):
    total = 5
    soFar = 0
    length = ''
    try:
        while(soFar < total):
            length += s.recv(total - soFar)
            soFar = len(length)
            if(soFar == 0):
                length = ''
                break;
    except:
        length = ''
    return length

