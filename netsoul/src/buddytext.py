
import curses

class   BuddyText:

    def __init__(self, root):
        self.root = root
        self.name = 'noname'
        self.buffer = ''
        self.__scroll = False
        self.__firstscroll = True
        self.iscroll = 0
        return 

    def rebuild(self, h, w, y, x):
        self.make(h, w, y, x)
        self.frame.addstr(self.buffer)

    def make(self, h, w, y, x):
        self.frame = curses.newpad(1024, w-2)
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

    def recv(self, text):
        self.pstr(self.name, curses.color_pair(1))
        self.pstr(' : ' + text + ' -- END\n')

    def send(self, text):
        self.pstr('YOU : ', curses.color_pair(1))
        self.pstr(text + ' -- END\n')

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
            

    def refresh(self):
        if (self.__scroll == False):
            yx = self.frame.getyx()
            if (yx[0] > self.h):
                self.frame.refresh(yx[0]-self.h, 0, self.y, self.x, self.h+2, self.w)
            else:
                self.frame.refresh(0, 0, self.y, self.x, self.h+2, self.w)
        else:
            self.frame.refresh(self.iscroll, 0, self.y, self.x, self.h+2, self.w)

    def top(self):
        #self.frame.redrawwin()
        self.refresh()
