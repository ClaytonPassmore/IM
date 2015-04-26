from message import formatMessage
from Tkinter import *

class convoWindow(Frame):
    def __init__(self, master=None, recip=None, user=None, sock=None, parent=None):
        Frame.__init__(self, master)
        self.pack(side='top', fill=BOTH, expand=True)
        self.master.bind('<Control-w>', self.die)
        self.recip = recip
        self.user = user
        self.sock = sock
        self.parent = parent
        self.userTag = 'usrTg'
        self.recipTag = 'recipTg'
        self.alertTag = 'alertTg'
        self.createWidgets()

    def die(self, event=None):
        self.parent.convos.pop(self.recip)
        self.master.destroy()

    def exists(self):
        return True

    def createWidgets(self):
        self.master.wm_protocol('WM_DELETE_WINDOW', self.die)
        self.master.title(self.recip)

        initText = 'New conversation with ' + self.recip + '\n'
        self.textWindow = Text(master=self, height=25, width=65, state=NORMAL, background='gray10')
        self.textWindow.tag_config(self.alertTag, foreground='red')
        self.textWindow.tag_config(self.userTag, foreground='blue')
        self.textWindow.tag_config(self.recipTag, foreground='green')
        self.textWindow.insert(END, initText, (self.alertTag,))
        self.textWindow.configure(state=DISABLED)

        self.inputFrame = Frame(master=self)

        self.textWindow.pack(side='top', fill=BOTH, expand=True)
        self.inputFrame.pack(side='top', fill=X, expand=False)

        self.inputText = StringVar()
        self.inputEntry = Entry(master=self.inputFrame, width=65, textvariable=self.inputText)
        self.inputEntry.bind('<Return>', self.submit)
        self.inputButton = Button(master=self.inputFrame, command=self.submit, text='Send')

        self.inputEntry.pack(side='left', fill=X, expand=True)
        self.inputButton.pack(side='left', expand=False)

        self.inputEntry.focus_set()

    def addText(self, sender, message):
        tag = self.alertTag
        if(sender == self.user):
            tag = self.userTag
        elif(sender == self.recip):
            tag = self.recipTag
        text = sender + ' says:\n    ' + message + '\n'
        self.textWindow.configure(state=NORMAL)
        self.textWindow.insert(END, text, (tag,))
        self.textWindow.see(END)
        self.textWindow.configure(state=DISABLED)

    def submit(self, event):
        msg = self.inputText.get()
        self.inputText.set('')
        text = '\\message;' + self.recip + ';' + msg
        if(len(msg) > 0):
            self.sock.send(formatMessage(text))
            self.addText(self.user, msg)

