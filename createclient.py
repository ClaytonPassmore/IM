import rsa
import socket
from message import formatMessage

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

    # Get user name and password
    user = raw_input('Enter a user name:\n')
    password = raw_input('Enter a password:\n')
    text = '\\newuser;' + user + ';' + password
    cipher = rsa.encrypt(text, publicKey)

    msg = formatMessage(cipher)
    s.send(msg)

    print(s.recv(2048))

    s.close()

if __name__ == '__main__':
    main()
