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

