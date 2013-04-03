from Tkinter import *
import time
import ns

MSGMUTEX = 0 # python mutex is useless win 2 thread
MSGARRAY = ['', '']

##
##  ulimit -s unlimited
##

class buddyWin(Frame):

    def putmessage(self, evt = ''):
        global MSGMUTEX
        global MSGARRAY

        mess = self.READBOX.get()
        self.READBOX.delete(ANCHOR, END)
        self.sendMessage(mess)
        while (MSGMUTEX == 1):
            time.sleep(0.05)
        MSGMUTEX = 1
        MSGARRAY = [self.name, mess]

    def createWidgets(self):

        self.BUDDYNAME = Label(self, text=self.name)
        self.BUDDYNAME.grid(row=1, column=0)

        self.BUDDYCOMMENTS = Label(self, text='dtc 10.0.0.1 - bnetsoul c\'est dla merde')
        self.BUDDYCOMMENTS.grid(row=1, column=1)
        
        self.BUDDYSTATUS = Label(self, text='(fx a poil)')
        self.BUDDYSTATUS.grid(row=1, column=2)


        self.INPUTBOX = Text(self)
        self.INPUTBOX.grid(row=2, column=1)

        #self.__input = StringVar()
        self.READBOX = Entry(self)
        #self.READBOX['textvariable'] = self.__input
        self.READBOX.bind('<Key-Return>', self.putmessage)
        self.READBOX['width'] = 70
        self.READBOX.grid(row=3, column=1)

        self.CLOSEWIN = Button(self)
        self.CLOSEWIN["text"] = "QUIT"
        self.CLOSEWIN["fg"]   = "red"
        self.CLOSEWIN["command"] =  self.quit
        self.CLOSEWIN.grid(row=3, column=0)

        self.SENDMSG = Button(self)
        self.SENDMSG["text"] = "SEND",
        self.SENDMSG["command"] = self.putmessage
        self.SENDMSG.grid(row=3, column=2)

        self.READBOX.focus_set()

    def getMessage(self, text):
        while (self.mutex == 1):
            time.sleep(0.05)
        self.mutex = 1
        self.INPUTBOX.insert(INSERT, "%s : %s\n" % (self.name, text))
        self.mutex = 0

    def sendMessage(self, text):
        while (self.mutex == 1):
            time.sleep(0.05)
        self.mutex = 1
        self.INPUTBOX.insert(INSERT, "YOU : %s\n" % (text))
        self.mutex = 0

    def buddyChangeStatus(self, status, buddy):

        if (status == 'actif' or status == 'login'):
            self.BUDDYNAME.config(fg='green')
            self.BUDDYSTATUS.config(fg='green')
        elif (status == 'away' or status == 'lock'):
            self.BUDDYNAME.config(fg='yellow')
            self.BUDDYSTATUS.config(fg='yellow')
        elif (status == 'logout'):
            self.BUDDYNAME.config(fg='red')
            self.BUDDYSTATUS.config(fg='red')
        else:
            self.BUDDYSTATUS.config(fg='purple')
            self.BUDDYNAME.config(fg='red')

        self.BUDDYCOMMENTS.config(text="%s %s - %s" % (buddy.location, buddy.fromIp, buddy.client))
        self.BUDDYSTATUS.config(text="(%s)" % status)

    def __init__(self, name):
        self.root = Tk()
        Frame.__init__(self, self.root)

        self.root.title('Buddy : ' + name)
        self.mutex = 0
        self.name = name
        self.pack()
        self.createWidgets()


class   TkwinMgr:

    def __init__(self):

        self.root = Tk()
        self.root.title('TcapEnTkSoul')
        self.buddys = {}
        self.frameroot = Tk()
        self.frame = Frame(self.root)
        self.buddylist = []

        self.LISTBOX = Listbox(self.frame, selectmode=SINGLE, width=30, height=20)  #, listvariable=self.lbvar)
        self.LISTBOX.bind("<Double-Button-1>", self.evtopenwin)
        self.frame.pack()
        self.LISTBOX.pack()

    def sendSysInfo(self, text):
        print 'SysInfo : ' + text


    def evtopenwin(self, id):
        buddyname =  self.LISTBOX.get(self.LISTBOX.curselection())
        self.openwin(buddyname)

    def openwin(self, name):
        self.buddys[name] = buddyWin(name)

    def addBuddy(self, buddy):
        
        self.LISTBOX.insert(END, buddy.fromName)
        self.buddylist.append(buddy.fromName)
        self.buddyChangeStatus(buddy)

    def buddyChangeStatus(self, buddy):

        try:
            self.buddys[buddy.fromName].buddyChangeStatus(buddy.state, buddy)
            print "%s change stat %s" % (buddy.fromName, buddy.state)
        except KeyError:
            print "%s change stat %s" % (buddy.fromName, buddy.state)

        i = self.buddylist.index(buddy.fromName)
        if (buddy.state == 'actif' or buddy.state == 'login'):
            self.LISTBOX.itemconfig(i, bg='green')
        elif (buddy.state == 'away' or buddy.state == 'lock'):
            self.LISTBOX.itemconfig(i, bg='yellow')
        elif (buddy.state == 'logout'):
            self.LISTBOX.itemconfig(i, bg='red')
        else:
            self.LISTBOX.itemconfig(i, bg='purple')


    def buddySendMsg(self, buddy):
        try:
            self.buddys[buddy.fromName].getMessage(buddy.msg)
        except:
            self.addBuddy(buddy)
            self.openwin(buddy.fromName)
            self.buddySendMsg(buddy)

    def destroy(self):
        return

    def read(self):             # Oui c'est moche blabla
        global MSGMUTEX
        global MSGARRAY
        
        while (MSGMUTEX == 0):  # sinon linux et curses ca marche
            time.sleep(0.01)     # tres bien windowsien a fenetre tout casser
                                # ca sera ameliorer plus tar
        buddyname = MSGARRAY[0]
        msg = MSGARRAY[1]
        MSGMUTEX = 0
        return (msg, buddyname)


import thread
def dede(win, f):
    win.root.mainloop()

def newwindow(conf):
    win = TkwinMgr()
    thread.start_new_thread(dede, (win, 0))
    return (win)
