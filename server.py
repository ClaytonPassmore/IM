import socket
import thread
from Queue import Queue
from socket_manager import socketManager
from incoming import manageIncoming
from listener import clientListener

"""
    Global socketManager
    Parent gets new connections and adds them to a queue
    Child 1 validates new connections from queue and adds them to socket manager
    Child 2 waits on and serves clients using select.
"""

# Start the server process
def main():
    # Manage sockets between threads
    socketMgr = socketManager()

    # Queue of new connections
    incomingQueue = Queue()

    # Start thread for handling new connections
    thread.start_new_thread(manageIncoming, (incomingQueue, socketMgr))

    # Start thread for listening to client requests
    thread.start_new_thread(clientListener, (socketMgr,))

    # Main server socket for incoming connections
    serverSocket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    # Bind the socket to a public host and well-known port
    serverSocket.bind((socket.gethostname(), 2048))
    serverSocket.listen(5)

    while True: 
        # Accept a client connection.
        (clientSocket, address) = serverSocket.accept()
        print "New client at " + str(address)

        # Put new socket in the new connection queue
        incomingQueue.put(clientSocket)

    # Clean up
    serverSocket.close()

if __name__ == '__main__':
    main()
