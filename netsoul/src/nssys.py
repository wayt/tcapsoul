
from buddytext import *

import curses
import tcsconfig

class   nssys:

    def __init__(self, root, nsc):
        self.nsc = nsc
        self.root = root
        self.echomode = True
        self.buffer = ''
        self.__scroll = False
        self.__firstscroll = True
        self.iscroll = 0
        self.__CommandsBind = list()
        self.autobindkey()
        return 


    def __PUSAGE_BINDKEY(self, key):
        self.pstr(key[2])

    def __bindKey_SAVE_func(self, text):
        text = text[5:]
        self.recv("LEN : %d" % len(text))
        conf = list()
        if (len(text) == 0):
            for bn in self.nsc.buddyList:
                conf.append(bn)
        else:
            conf = text.replace(' ', '').split(',')
        tcsconfig.saveBuddyList(conf)
        self.recv('Buddy List saved : %s' % conf)
        return (0)

    def __bindKey_SAVE_help(self, text):
        self.recv('This function save the current buddy list or a buddy or a list of buddy')
        self.recv('USAGE : save [buddyname1, buddyname2, ...]')
        self.recv(' ')
        return (0)

    def __bindKey_HELP_func(self, text):

        if (text == 'help'):
            text = 'help help'
        command = text.split(' ')[1]
        for name, func, com  in self.__CommandsBind:
            if (name == command):
                com(text)
                return (0)
        self.recv('Command not found %s' % command)
        return (0)

    def __bindKey_HELP_help(self, text):

        self.recv('USAGE : help [command] [commands options] :')
        self.recv('\t-command list : ')
        for name, func, com  in self.__CommandsBind:
            self.recv('-%s' % name)

    def __bindKey_STATE_func(self, text):
        self.nsc.sendState(text[6:])

    def __bindKey_STATE_help(self, text):
        self.recv('USAGE: state new_status')
        self.recv('Status may be :')
        self.recv('\t-actif ')
        self.recv('\t-away ')
        self.recv('\t-lock ')
        self.recv('')

    def __bindKey_CP_func(self, text):
        c = text.split(' ')[1]
        if (c == 's'):
            i = text.rfind(' ')
            buddy = text[i:]
            file = text[len('cp s '):len(text)-i]
            av = ['nsssys-cp', 's', file, buddy]
        else:
            av = text.split(' ')

        EXTRA_COPYFILE.PSTR = self.recv
        EXTRA_COPYFILE.ARGV = av
        EXTRA_COPYFILE.start()

    def __bindKey_CP_help(self, text):
        self.recv('CP : put/get file to/from login.')
        self.recv('USAGE : ')


    def __bindKey_ECHO_func(self, text):
        text = text.replace('\\n', '\n').replace('\\t', '\t')
        if (text[5:] == 'on'):
            self.echomode = True
            self.recv('Passing to echo on')
        elif (text[5:] == 'off'):
            self.echomode = False
            self.recv('Passing to echo off')
        else:
            self.pstr(text[5:])

    def __bindKey_ECHO_help(self, text):
        self.recv('USAGE echo message')
        self.recv('\t-To stop/start the echo you can put "echo off/on (by default on)')
        self.recv(' ')

    def __bindKey_ADD_func(self, text):
        self.nsc.addBuddy(text.split(' ')[1], flush=True)

    def __bindKey_ADD_help(self, text):
        self.recv('USAGE add login')
        self.recv('\t-Add login to buddy list')
        self.recv(' ')

    def autobindkey(self):
        self.__CommandsBind.append(['help', self.__bindKey_HELP_func, self.__bindKey_HELP_help])
        self.__CommandsBind.append(['state', self.__bindKey_STATE_func, self.__bindKey_STATE_help])
        self.__CommandsBind.append(['echo', self.__bindKey_ECHO_func, self.__bindKey_ECHO_help])
        self.__CommandsBind.append(['add', self.__bindKey_ADD_func, self.__bindKey_ADD_help])
        self.__CommandsBind.append(['save', self.__bindKey_SAVE_func, self.__bindKey_SAVE_help])

    def rebuild(self, h, w, y, x):
        self.make(h, w, y, x)
        self.frame.addstr(self.buffer)

    def make(self, h, w, y, x):
        self.frame = curses.newpad(1024, w)
        self.y = y+1
        self.x = x+1
        self.w = w-2
        self.h = h-2

        self.frameBox = curses.newwin(h, w, y, x)
        self.frameBox.box()
        self.frameBox.refresh()
        self.refresh()

    def pstr(self, text, flags = ''):
        self.buffer += text # Il faudra le flush un jour...
        if (flags == ''):
            self.frame.addstr(text)
        else:
            self.frame.addstr(text, flags)

    def send(self, text):

        if (self.echomode == True):
            self.pstr('YOU', curses.color_pair(1))
            self.pstr('    : ' + text + '\n')
        command = text.split(' ')[0]
        for name, func, com  in self.__CommandsBind:
            if (name == command):
                return (func(text))
        self.pstr('Command not found : "%s" -->%s<--\n' % (command, text))
        return (1)

    def recv(self, text):
        self.pstr('NS-SYS', curses.color_pair(1))
        self.pstr(' : ' + text + '\n')
        #self.refresh()

    def refresh(self):
        if (self.__scroll == False):
            yx = self.frame.getyx()
            if (yx[0] > self.h):
                self.frame.refresh(yx[0]-self.h, 0, self.y, self.x, self.h+2, self.w)
            else:
                self.frame.refresh(0, 0, self.y, self.x, self.h, self.w)
        else:
            self.frame.refresh(self.iscroll-self.h, 0, self.y, self.x, self.h, self.w)


    def top(self):
        #self.frame.redrawwin()
        self.refresh()

    def scroll(self, i):
        y = self.frame.getyx()[0] - self.h
        if (self.__firstscroll == True):
            self.iscroll = y 
            self.__firstscroll = False
            self.__scroll = True

        self.iscroll += i
        if (self.iscroll < 0):
            self.iscroll = 0
        elif (self.iscroll > y):
            self.__scroll = False
            self.__firstscroll = True
