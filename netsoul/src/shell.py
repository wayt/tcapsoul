##
##  YO SHELL MODE
##
##

import os
import cmd

CAP_BLINK = '\033[5m'
CAP_NORMAL = '\033[0m'
CAP_BOLD = '\033[1m'
CAP_UNDERLINE = '\033[4m'

FG_BLACK = '\033[30m'
FG_RED = '\033[31m'
FG_GREEN = '\033[32m'
FG_YELLOW = '\033[33m'
FG_BLUE = '\033[34m'
FG_PURPLE = '\033[35m'
FG_CYIAN = '\033[36m'
FG_GREY = '\033[37m'
FG_CURRENT = '\033[38m'
FG_WHITE = '\033[39m'

BG_BLACK = '\033[40m'
BG_RED = '\033[41m'
BG_GREEN = '\033[42m'
BG_YELLOW = '\033[43m'
BG_BLUE = '\033[44m'
BG_PURPLE = '\033[45m'
BG_CYIAN = '\033[46m'
BG_GREY = '\033[47m'
BG_CURRENT = '\033[48m'
BG_WHITE = '\033[49m'

#for i, buddy in enumerate(self.current.buddylist): ---->>> for list

FG_NORMAL = FG_GREY
BG_NORMAL = BG_BLACK

class   handleEX(BaseException):

    def __init__(self, name, msg):

        BaseException.__init__(self)
        self.name = name
        self.msg = msg

class   Commands(cmd.Cmd):

    def     __init__(self, current):

        cmd.Cmd.__init__(self)
        self.current = current

    def     complete_buddyname(self, text, line, begx, endx):
        rettab = []
        l = line[begx:]
        for name, buddy in self.current.buddylist.iteritems():
            if (name.find(l) != -1):
                rettab.append(name)
        return (rettab)


    ########### listage des buddy #############

    def     listabuddy(self, buddy, i):
        if (buddy.state == 'actif' or buddy.state == 'login'):
            color = FG_GREEN
        elif (buddy.state == 'away' or buddy.state == 'idle' or buddy.state == 'lock'):
            color = FG_YELLOW
        elif (buddy.state == 'logout'):
            color = FG_RED
        else:
            color = FG_PURPLE
        if (buddy.haveMsg == True):
            print "%s(%d) %s%s%s\tstate:%s\tlocation:%s\tclient:%s\tip:%s%s" % (BG_BLUE+CAP_BLINK, i, color, buddy.fromName, FG_NORMAL, buddy.state, buddy.location, buddy.client, buddy.fromIp, BG_NORMAL+CAP_NORMAL)
        else:
            print "(%d) %s%s%s\tstate:%s\tlocation:%s\tclient:%s\tip:%s" % (i, color, buddy.fromName, FG_NORMAL, buddy.state, buddy.location, buddy.client, buddy.fromIp)

    def     complete_listbuddy(self, text, line, begx, endx):
        return (self.complete_buddyname(text, line, begx, endx))

    def     help_listbuddy(self):
        print 'list a/all buddy'
        print 'USAGE : listbuddy [login]'
        print ''

    def     do_listbuddy(self, line):

        print 'buddy list :'
        i = 0
        for name, buddy in self.current.buddylist.iteritems():
            if (line == '' or line == name):
                self.listabuddy(buddy, i)
            i += 1
        print 'done'
        return (0)


    ############# Recuperation des message d'un buddy ##############

    def         help_getmsg(self):
        print 'get messages from buddy'
        print 'USAGE : getmsg login'
        print ''

    def         complete_getmsg(self, text, line, begx, endx):
        return (self.complete_buddyname(text, line, begx, endx))

    def         do_getmsg(self, line):
        try:
            print self.current.buddylist[line].msg
            self.current.buddylist[line].msg = ''
            self.current.buddylist[line].haveMsg = False
        except:
            print 'Buddy not exist...'
        return (0)

    ############## Gestion d'envoi ################

    def         help_send(self):
        print 'send a message to a buddy'
        print 'USAGE : send login message'
        print ''

    def         do_send(self, line):
        tmp = line.split(' ')
        line = ' '.join(tmp[1:])
        raise handleEX(tmp[0], line) # megamegagore

    def         complete_send(self, text, line, begx, endx):
        return (self.complete_buddyname(text, line, begx, endx))

    def         complete_s(self, text, line, begx, endx):
        return (self.complete_buddyname(text, line, begx, endx))

    def         do_s(self, line):
        self.do_send(line)


class shellMgr:

    def __init__(self):
        self.buffer = ''
        self.event_stack = ''
        self.msg_stack = ''
        self.buddylist = {}


        self.commands = []
        self.sh = Commands(self)
        self.sh.prompt = 'shell>'


    def pstr(self, text):
        os.write(1, text)

    def sendSysInfo(self, text):
        self.event_stack += '___SYSTEM___ : ' + text
        
    def addBuddy(self, buddy):
        self.event_stack += 'NEW BUDDY :' + buddy.fromName + '\n'
        self.buddylist[buddy.fromName] = buddy
        self.buddylist[buddy.fromName].lastmsg = ''
        self.buddylist[buddy.fromName].haveMsg = False

    def buddyChangeStatus(self, buddy):
        self.event_stack += "%s change state to %s\n" % (buddy.fromName, buddy.state)

        self.buddylist[buddy.fromName].fromName = buddy.fromName
        self.buddylist[buddy.fromName].state = buddy.state
        self.buddylist[buddy.fromName].client = buddy.client
        self.buddylist[buddy.fromName].fromIp = buddy.fromIp
        self.buddylist[buddy.fromName].location = buddy.location


    def buddySendMsg(self, buddy):
        buddy.msg = "%s : %s\n" % (buddy.fromName, buddy.msg)
        self.buddylist[buddy.fromName].msg += buddy.msg
        self.buddylist[buddy.fromName].haveMsg = True
        self.event_stack += "%s : %s\n" % (buddy.fromName.upper(), buddy.msg)


    def loop(self):

        while (1):
            try:
                argc, argv = self.sh.cmdloop()
            except handleEX as e:
                return (e.msg, e.name)
        return ('')

    def read(self):
                    
        msg, buddy = self.loop()
        self.pstr("TO %s : %s\n" % (buddy, msg))
        return (msg, buddy)

    def destroy(self):
        return

def newwindow(conf):
    win = shellMgr()
    return (win)
