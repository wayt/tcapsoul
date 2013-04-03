import curses
import time
import signal
import fcntl
import termios
import struct
import os
import nssys
import traceback
import sys

from buddylist import *
from buddytext import *
from infobar import *

import tcapsoulAPI as tcs

class   MainWindow(tcs.TcapsoulAPI):

    def __init__(self, scr_root):
        self.root = scr_root
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK) #// Msg
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) #// actif
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) #// idle
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK) #// logout
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) #// don't know
        #signal.signal(signal.SIGWINCH, self.handle)
        self.buddysWindow = dict()
        self.nssys = tcs.BuddyObject('ns-sys')
        self.currentBuddy = 'ns-sys'
        self.__makeWindow()
        self.buddysWindow[self.currentBuddy] = nssys.nssys(self.root, self)
        self.makeBuddyWindow(self.currentBuddy)
        self.buddysId = ['ns-sys']
        tcs.TcapsoulAPI.__init__(self, self.sendSysInfo)

    def getCurrentBuddy(self):
        return (self.currentBuddy)

    def sendSysInfo(self, text):
        self.buddysWindow['ns-sys'].recv(text)
        if ('ns-sys' == self.currentBuddy):
            self.buddysWindow['ns-sys'].refresh()

    def changeBuddy(self, id):
        if (id < len(self.bl.list)):
            if (id == 0):
                self.currentBuddy = 'ns-sys'
            else:
                self.currentBuddy = self.buddyList[self.buddysId[id]][0].name
            self.buddysWindow[self.currentBuddy].top()
            if (self.bl.isSelected(id) == True):
                self.bl.unselectBuddy(id)
            self.bl.focusBuddy(id)
            return (True)
        self.changeBuddy(0)
        return (False)

    def buddyChangeStatus(self, buddy):
        self.sendSysInfo("Buddy Change status : %s : %s" % (buddy.name, buddy.state))
        id = self.getBuddyId(buddy)
        if (buddy.name == self.currentBuddy):
            self.ib.currentBuddy(buddy)
        self.bl.changeBuddyStatus(id, buddy.state)
        self.bl.refresh()

    def buddySendMessage(self, buddy, message):
        
        id = self.getBuddyId(buddy)
        self.buddysWindow[buddy.name].recv(message)
        if (buddy.name != self.currentBuddy):
            self.bl.selectBuddy(id)
        else:
            self.buddysWindow[self.currentBuddy].refresh()


    def newBuddy(self, buddy):
        self.buddysWindow[buddy.name] = BuddyText(self.root)
        self.buddysId.append(buddy.name)
        self.makeBuddyWindow(buddy.name)
        self.bl.addBuddy(buddy.name)
        #self.bl.focusBuddy(0)


    def getBuddyId(self, buddy):
        try:
            id = self.buddysId.index(buddy.name)
        except:
            self.newBuddy(buddy)
            id = len(self.buddysId) - 1
        return (id)

    def getTermSize(self):
        return (self.__ioctl_GWINSZ(0))

    def handle(self):
        y, x = self.getTermSize()
        blx = x - WIN_BUDDYLIST_SIZEX


        self.bl.root = self.root
        self.bl.make(y-3, WIN_BUDDYLIST_SIZEX, 2, blx)
        self.bl.wrefresh()

        self.ib.mutex(True)
        self.ib.root = self.root
        self.ib.make(1, x, 1, 1)
        self.ib.refresh()
        self.ib.mutex(False)

        self.rl.root = self.root
        self.rl.rebuild(x, y)

        for name, w in self.buddysWindow.iteritems():
            w.root = self.root
            w.rebuild(y-3, blx-4, 2, 1)
        self.buddysWindow[self.currentBuddy].top()


    def makeBuddyWindow(self, buddy):
        bw = self.buddysWindow[buddy]
        y, x = self.getTermSize()
        blx = x - WIN_BUDDYLIST_SIZEX
        bw.make(y-3, blx-4, 2, 1)
        bw.name = buddy
    
    def refreshWindow(self):
        self.buddysWindow[self.currentBuddy].refresh()
        self.ib.refresh()

    ###
    ### INTERNAL
    ###

    def __makeWindow(self):

        self.testTermSize()
        y, x = self.getTermSize()
        blx = x - WIN_BUDDYLIST_SIZEX
        # BuddyList
        self.bl = BuddyList(self.root)
        self.bl.make(y-3, WIN_BUDDYLIST_SIZEX, 2, blx)
        #self.bl.wrefresh()
        self.bl.addBuddy('ns-sys')
        self.bl.focusBuddy(0)
        # InfoBar
        self.ib = InfoBar(self.root)
        self.ib.make(1, x, 1, 1)
        self.ib.refresh()
        # readline Un jour dans buddyText
        self.rl = readLines(self.root, self)
        self.rl.make(x, y)


    def testTermSize(self):
        y, x = self.getTermSize()
        if (x < WIN_BUDDYLIST_SIZEX + 40 or y < 7):
            raise tcs.TcapsoulException('Too small term')
        return (0)
        
    def __ioctl_GWINSZ(self, fd):
        try:
            winsz = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return None
        return winsz

class   readLines:

    def __init__(self, root, tcs):
        self.tcs = tcs
        self.root = root
        self.bindkeys = []
        self.addBindkey(127, self.__backspace, [])
        self.addBindkey(curses.KEY_BACKSPACE, self.__backspace, [])
        self.addBindkey(curses.KEY_LEFT, self.__left_key, [])
        self.addBindkey(curses.KEY_RIGHT, self.__right_key, [])


        self.addBindkey(curses.KEY_NPAGE, self.__scroll, [1])
        self.addBindkey(curses.KEY_PPAGE, self.__scroll, [-1])

    def __scroll(self, s, args):
        self.tcs.buddysWindow[self.tcs.currentBuddy].scroll(args[0])
        self.tcs.buddysWindow[self.tcs.currentBuddy].refresh()

    def __mouse_event(self, s, args):
        b = curses.getmouse()
        if (b[4] == 524288):
            self.tcs.buddysWindow[self.tcs.currentBuddy].scroll(-1)
        elif (b[4] == 134217728):
            self.tcs.buddysWindow[self.tcs.currentBuddy].scroll(1)
        self.tcs.buddysWindow[self.tcs.currentBuddy].refresh()

    def __backspace(self, s, args):

        if (self.xy[1] > self.lprompt):
            self.message = self.message[:self.xy[1]-self.lprompt-1] + self.message[self.xy[1]-self.lprompt:]
            self.xy[1] -= 1
            self.winReadLine.delch(self.xy[0], self.xy[1])
            
        
    def __left_key(self, s, args):
        if (self.xy[1] > self.lprompt):
            self.xy[1] -= 1
            self.winReadLine.move(self.xy[0], self.xy[1])

    def __right_key(self, s, args):
        if (self.xy[1] - self.lprompt < len(self.message)):
            self.xy[1] += 1
            self.winReadLine.move(self.xy[0], self.xy[1])

    def rebuild(self, x, y):
        #self.winReadLine.destroy()
        self.make(x, y)

    def make(self, x, y):
        self.winReadLine = curses.newwin(1, x, y-1, 0)
        self.winReadLine.keypad(1)

    def addBindkey(self, key, f, args):
        self.bindkeys.append([key, f, args])

    def refresh(self):
        self.winReadLine.refresh()

    def read(self, prompt = '>>>'):
        if (self.tcs.conf.mouseScroll == True):
            curses.mousemask(curses.BUTTON_SHIFT | curses.BUTTON_CTRL | curses.BUTTON_ALT | curses.BUTTON4_PRESSED | curses.BUTTON4_RELEASED)
            curses.mouseinterval(5)
            self.addBindkey(curses.KEY_MOUSE, self.__mouse_event, [])


        self.prompt = prompt
        self.winReadLine.addstr(prompt)
        self.message = ''
        found = 0
        fxy = self.winReadLine.getyx()
        self.xy = [fxy[0], len(prompt)]
        self.lprompt = len(self.prompt)
        while 1:
            ch = self.winReadLine.getch()
            for key, f, args in self.bindkeys:
                if (key == ch):
                    f(self, args)
                    found = 1
                    break
            if (found == 1):
                found = 0
                continue
            if (ch == 10):
                if (self.tcs.currentBuddy != 'ns-sys'):
                    self.tcs.sendToLogin(self.tcs.currentBuddy, self.message)
                self.tcs.buddysWindow[self.tcs.currentBuddy].send(self.message)
                self.tcs.buddysWindow[self.tcs.currentBuddy].refresh()

                self.xy[1] = self.lprompt - 1
                self.winReadLine.move(self.xy[0], self.xy[1]+1)
                #self.winReadLine.addstr(self.prompt)
                self.winReadLine.clrtoeol()
                self.message = ''
            elif (ch <= 255 and ch >= 0):
                if (self.xy[1] - self.lprompt != len(self.message)):
                    self.message = self.message[:self.xy[1]-self.lprompt] + chr(ch) + self.message[self.xy[1]-self.lprompt:]
                else:
                    self.message += chr(ch)
            else:
                continue
            self.winReadLine.insch(ch)
            self.xy[1] += 1
            self.winReadLine.move(self.xy[0], self.xy[1])

    def getKey(self):
        ch = self.winReadLine.getch()
        return (ch)




##
## --- SYSTEM ---
##
##

III = 0

def     changeBuddy(rl, arg):
    global III

    win = arg[0]
    i = arg[1]

    if (i == 1):
        III += 1
    elif (III != 0):
        III -= 1
    else:
        III = len(win.bl.list) - 1

    if (win.changeBuddy(III) == False):
        III = 0
    rl.lprompt = len(win.getCurrentBuddy()+'>>>')
    rl.prompt = win.getCurrentBuddy()+'>>>'
    rl.winReadLine.addstr(0, 0, rl.prompt)
    rl.xy[1] = rl.lprompt
    rl.message = ''
    rl.winReadLine.move(rl.xy[0], rl.xy[1])
    rl.winReadLine.clrtoeol()
    
    if (III != 0):
        win.ib.currentBuddy(win.buddyList[win.currentBuddy][0])
    else:
        win.ib.currentBuddy(win.nssys)
    win.ib.refresh()
    return 

def winresize(rl, arg):
    arg[0].ib.mutex(True)
    arg[0].root.clear()
    arg[0].root.refresh()

    while 1:
        try:
            arg[0].testTermSize()
            break
        except tcs.TcapsoulException as e:
            print 'TERMINAL TROP PETIT\n'
            print 'TERMINAL TROP PETIT\n'
            print 'TERMINAL TROP PETIT\n'
        while 1:
            char = rl.winReadLine.getch()
            if (char == curses.KEY_RESIZE):
                break

    arg[0].ib.mutex(False)
    arg[0].handle()
    arg[0].sendSysInfo('WINDOW RESIZE')

def newwindow(scr):
    win = MainWindow(scr)
    win.rl.addBindkey(curses.KEY_RESIZE, winresize, [win])
    win.rl.addBindkey(9, changeBuddy, [win, 1])
    win.rl.addBindkey(curses.KEY_DOWN, changeBuddy, [win, 1])
    win.rl.addBindkey(curses.KEY_UP, changeBuddy, [win, 0])
    win.buddysWindow['ns-sys'].top()
    win.refreshWindow()
    win.start()
    
    try:
        win.rl.read()
    except KeyboardInterrupt:
        if (win.conf.mouseScroll == True):
            curses.mouseinterval(200)
        curses.endwin()
    except tcs.TcapsoulException as e:
        if (win.conf.mouseScroll == True):
            curses.mouseinterval(200)
        curses.endwin()
        print '\n\n\nVous avez fait quelque chose de mal : "%s"' % e.message
    except:
        if (win.conf.mouseScroll == True):
            curses.mouseinterval(200)
        curses.endwin()
        print "\033[31m !!!!!! OOOOOoops TCAPSOUL a plante !!!!!!\033[37m"
        #res = raw_input('Voulez vous voir pourquoi? (o/n)')
        #if (res[0:1] == 'o'):
        traceback.print_exc(file=sys.stdout)
    print '-----------------------TCAPSOUL BETA 1-----------------------------'
    print "Bye bye - n'oubliez pas d'enculer a sec branda_f si vous le voyez!"
    return (0)

def     INIT():
    curses.wrapper(newwindow)

if __name__ == "__main__":
    INIT()
