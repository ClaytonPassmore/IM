import socket

def main():
    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    # Connect to the server
    s.connect((socket.gethostname(), 2048))

    # Send identifier to server
    ident = 'ctpassmore'
    length = len(ident)
    msg = ('%05d' % length) + ident
    s.send(msg)

    while True:
        text = raw_input('Enter a message:\n')
        length = len(text)
        if(length == 0):
            break

        msg = ('%05d' % length) + text
        s.send(msg)

if __name__ == '__main__':
    main()
