import rsa
import socket
import thread
from message import fetchMessage, formatMessage, getMessageLengthString

def listen(sock):
    while True:
        length = getMessageLengthString(sock)
        if(len(length) == 0):
            sock.close()
            print 'Disconnected'
            return
        result = fetchMessage(int(length), sock)
        print result

def main():
    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    with open('keys/public.pem', 'r') as publicFile:
        keyData = publicFile.read()
    publicKey = rsa.PublicKey.load_pkcs1(keyData)

    # Connect to the server
    s.connect((socket.gethostname(), 2048))

    # Attempt to connect to server
    ident = raw_input("Username:\n")
    password = raw_input("Password:\n")
    while((' ' in ident) or (' ' in password) or (';' in ident)):
        print "Invalid, try again."
        ident = raw_input("Username:\n")
        password = raw_input("Password:\n")

    if(ident == '' or password == ''):
        return

    text = '\\connect;' + ident + ';' + password

    # Encrypt message
    cipher = rsa.encrypt(text, publicKey)
    msg = formatMessage(cipher)
    s.send(msg)

    # Get server response
    length = getMessageLengthString(s)
    if(len(length) == 0):
        s.close()
        print 'Disconnected'
        return
    result = fetchMessage(int(length), s)

    # Verify server
    expected = '\\status;1;\\connect;' + ident + ';'
    if(result <= len(expected)):
        print "Unexpected server response ... disconnecting"
    signature = result[len(expected):]
    result = result[0:len(expected)-1]
    try:
        rsa.verify(result, signature, publicKey)
    except:
        print "Could not verify server ... disconnecting"
        s.close()
        return
    print "Server verified. Connection established."

    # Create listening thread
    thread.start_new_thread(listen, (s,))

    while True:
        text = raw_input('Enter a message:\n')
        if(text == ''):
            break

        msg = formatMessage(text)
        s.send(msg)

if __name__ == '__main__':
    main()
