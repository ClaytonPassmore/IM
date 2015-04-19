import socket
import sys
import thread
from message import fetchMessage, formatMessage, getMessageLengthString

def listen(sock):
    while True:
        result = sock.recv(2048)
        if(len(result) == 0):
            sock.close()
            return
        print result

def main(args):
    if(len(args) < 3):
        return
    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    # Connect to the server
    s.connect((socket.gethostname(), 2048))

    # Create listening thread
    thread.start_new_thread(listen, (s,))

    # Send identifier to server
    ident = args[1]
    password = args[2]
    text = '\\connect;' + ident + ';' + password
    length = len(text)
    msg = ('%05d' % length) + text
    s.send(msg)

    while True:
        text = raw_input('Enter a message:\n')
        length = len(text)
        if(length == 0):
            break

        msg = ('%05d' % length) + text
        s.send(msg)

if __name__ == '__main__':
    main(sys.argv)
