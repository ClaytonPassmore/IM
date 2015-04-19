import socket

def main():
    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    # Connect to the server
    s.connect((socket.gethostname(), 2048))

    # Get user name and password
    user = raw_input('Enter a user name:\n')
    password = raw_input('Enter a password:\n')
    text = '\\newuser;' + user + ';' + password
    length = len(text)

    msg = ('%05d' % length) + text
    s.send(msg)

    if(s.recv(1) == '1'):
        print "Success!"
    else:
        print user + " is already taken"

    s.close()

if __name__ == '__main__':
    main()
