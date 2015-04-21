import sys
import rsa
import socket
import thread
from message import fetchMessage, formatMessage, getMessageLengthString

def listen(sock):
    while True:
        length = getMessageLengthString(sock)
        if(len(length) == 0):
            sock.close()
            return
        result = fetchMessage(int(length), sock)
        print result

def main(args):
    if(len(args) < 3):
        return
    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    with open('keys/public.pem', 'r') as publicFile:
        keyData = publicFile.read()
    publicKey = rsa.PublicKey.load_pkcs1(keyData)

    # Connect to the server
    s.connect((socket.gethostname(), 2048))

    # Create listening thread
    thread.start_new_thread(listen, (s,))

    # Send identifier to server
    ident = args[1]
    password = args[2]
    text = '\\connect;' + ident + ';' + password
    cipher = rsa.encrypt(text, publicKey)
    msg = formatMessage(cipher)
    s.send(msg)

    while True:
        text = raw_input('Enter a message:\n')
        if(text == ''):
            break

        msg = formatMessage(text)
        s.send(msg)

if __name__ == '__main__':
    main(sys.argv)
