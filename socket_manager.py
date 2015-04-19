"""
    Manage a two-way dictionary of sockets and labels.
    Methods:
        addSocket
        removeSocket
        removeLayer
        getSocket
        getLabel
        getSockets
        getLabels
"""
class socketManager():
    def __init__(self):
        self.labels = {}
        self.sockets = {}

    def addSocket(self, socket, label):
        self.labels[socket] = label
        self.sockets[label] = socket

    def removeSocket(self, socket):
        if(socket in self.labels.keys()):
            label = self.labels[socket]
            if(label in self.sockets.keys()):
                self.sockets[label].close()
                del self.sockets[label]
            del self.labels[socket]

    def removeLabel(self, label):
        if(label in self.sockets.keys()):
            socket = self.sockets[label]
            if(socket in self.labels.keys()):
                del self.labels[socket]
            self.sockets[label].close()
            del self.sockets[label]

    def getSocket(self, label):
        if(label in self.sockets.keys()):
            return self.sockets[label]
        return False

    def getLabel(self, socket):
        if(socket in self.labels.keys()):
            return self.labels[socket]
        return False

    def getSockets(self):
        return self.sockets.values()

    def getLabels(self):
        return self.labels.values()
