import rsa
import time
import socket
import thread
from Tkinter import *
from ast import literal_eval
from Queue import Queue
from convowindow import convoWindow
from message import fetchMessage, formatMessage, getMessageLengthString

class Application(Frame):
    def die(self, event=None):
        self.sock.close()
        self.quit()

    def requestContacts(self):
        while True:
            text = '\\contacts'
            msg = formatMessage(text)
            self.sock.send(msg)
            time.sleep(4)


    def updateContacts(self):
        self.listBox.delete(0, END)
        for i in range(len(self.contacts)):
            entry = self.contacts[i][2] + ' ' + self.contacts[i][1] + ' - ' + self.contacts[i][0]
            self.listBox.insert(i, entry)

    def listen(self, sock):
        while True:
            length = getMessageLengthString(sock)
            if(len(length) == 0):
                sock.close()
                print 'Disconnected'
                self.quit()
            result = fetchMessage(int(length), sock)
            if(len(result) > len('\\contacts;') and result[:10] == '\\contacts;'):
                self.contacts = literal_eval(result[10:])
                self.updateContacts()
            elif(len(result) > len('\\message;') and result[:9] == '\\message;'):
                self.msgQueue.put(result[9:])
            else:
                print result

    def createWidgets(self):
        # Contact list to be displayed after log in
        self.listBox = Listbox(master=self, height=30, selectmode=SINGLE, width=50, activestyle='dotbox')
        self.listBox.bind('<Double-Button-1>', self.convoFromSelection)

        # Widgets to display now
        self.userLabel = Label(master=self, text='Username:')
        self.passLabel = Label(master=self, text='Password:')
        self.userText = StringVar()
        self.passText = StringVar()
        self.userEntry = Entry(master=self, width=50, textvariable=self.userText)
        self.passEntry = Entry(master=self, width=50, textvariable=self.passText, show='*')
        self.submitButton = Button(master=self, text='Login', command=self.login)
        self.userLabel.pack(side='top')
        self.userEntry.pack(side='top', padx=10)
        self.passLabel.pack(side='top')
        self.passEntry.pack(side='top', padx=10)
        self.submitButton.pack(side='top')

        self.userEntry.bind('<Return>', self.login)
        self.passEntry.bind('<Return>', self.login)
        self.userEntry.focus_set()

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.bind('<Control-w>', self.die)
        self.pack(fill='both', expand=True)
        self.convos = {}
        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.msgQueue = Queue()

        # Get our public key
        with open('keys/public.pem', 'r') as publicFile:
            keyData = publicFile.read()
        self.publicKey = rsa.PublicKey.load_pkcs1(keyData)

        # Create widgets
        self.createWidgets()


    def login(self, event=None):
        # Connect to the server
        self.sock.connect((socket.gethostname(), 2048))

        # Attempt to connect to server
        self.user = self.userText.get()
        password = self.passText.get()

        text = '\\connect;' + self.user + ';' + password

        # Encrypt message
        cipher = rsa.encrypt(text, self.publicKey)
        msg = formatMessage(cipher)
        self.sock.send(msg)

        # Get server response
        length = getMessageLengthString(self.sock)
        if(len(length) == 0):
            self.sock.close()
            print 'Disconnected'
            self.quit()
        result = fetchMessage(int(length), self.sock)

        # Verify server
        expected = '\\status;1;\\connect;' + self.user + ';'
        if(result <= len(expected)):
            print "Unexpected server response ... disconnecting"
        signature = result[len(expected):]
        result = result[0:len(expected)-1]
        try:
            rsa.verify(result, signature, self.publicKey)
        except:
            print "Could not verify server ... disconnecting"
            self.sock.close()
            self.quit()
        print "Server verified. Connection established."

        # Create listening thread
        thread.start_new_thread(self.listen, (self.sock,))

        # Populate the contact list
        thread.start_new_thread(self.requestContacts, ())

        self.userLabel.pack_forget()
        self.userEntry.pack_forget()
        self.passLabel.pack_forget()
        self.passEntry.pack_forget()
        self.submitButton.pack_forget()

        # Change state
        self.master.title('Contacts')
        self.listBox.pack(fill=BOTH, expand=True, padx=5, pady=5)

    def incomingMessages(self):
        message = None
        try:
            message = self.msgQueue.get_nowait()
        except:
            # Reschedule ourself
            root.after(1, self.incomingMessages)
            return
        ident = message.split(';')[0]
        msg = message[(len(ident)+1):]
        if(ident not in self.convos.keys()):
            self.convos[ident] = convoWindow(master=Toplevel(self), recip=ident, user=self.user, sock=self.sock, parent=self)
        self.convos[ident].addText(ident, msg)

        # Reschedule ourself
        root.after(0, self.incomingMessages)


    def convoFromSelection(self, event):
        idxs = self.listBox.curselection()
        if(len(idxs) == 0):
            return
        idx = idxs[0]
        contact = self.contacts[idx]
        if(contact[2] == '0'):
            return
        ident = contact[0]
        if(ident not in self.convos.keys()):
            self.convos[ident] = convoWindow(master=Toplevel(self), recip=ident, user=self.user, sock=self.sock, parent=self)

if __name__ == '__main__':
    root = Tk()
    app = Application(master=root)
    root.protocol('WM_DELETE_WINDOW', app.die)
    root.title('IM')
    root.after(0, app.incomingMessages)
    app.mainloop()
    root.destroy()

