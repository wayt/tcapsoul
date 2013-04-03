
import curses

WIN_BUDDYLIST_SIZEX = 10

class   BuddyList:

    def __init__(self, root):
        self.root = root
        self.list = []
        self.selected = []
        self.lastFocus = 0
        self.width = 0
        self.iscroll = 0
        self.used = 0

    def make(self, h, w, y, x):
        self.h = h-2
        self.w = w-2
        self.y = y+1
        self.x = x+1

        self.frame = curses.newpad(512, 64)

        self.frameBox = curses.newwin(h, w, y, x)
        self.frameBox.box()
        self.frameBox.refresh()

    def getBuddyName(self, id):
        return (self.list[id][0])

    def getBuddyState(self, id):
        return (self.list[id][1])

    def addBuddy(self, login):
        i = len(self.list)
        self.list.append([login, curses.color_pair(4), 0])
        self.pstr(i, self.getBuddyName(i))
        self.refresh()

    def removeBuddy(self, id):
        self.list.remove(id)
        return (False)

    def selectBuddy(self, i):
        self.pstr(i, self.getBuddyName(i), curses.A_BLINK | curses.A_REVERSE | curses.A_BOLD)
        self.selected.append(i)
        self.list[i][2] = 1
        self.refresh()
        return

    def unselectBuddy(self, i):
        self.pstr(i, self.getBuddyName(i))
        self.list[i][2] = 0
        self.selected.remove(i)
        self.refresh()
        return

    def focusBuddy(self, i):
        self.pstr(self.lastFocus, self.getBuddyName(self.lastFocus))
        self.lastFocus = i
        if (i >= self.iscroll + self.h -1):
            self.iscroll = i - self.h + 1
        elif (i < self.iscroll):
            self.iscroll = i
        self.pstr(i, self.getBuddyName(i), curses.A_UNDERLINE | curses.A_BOLD)
        self.refresh()
        return

    def changeBuddyStatus(self, id, status):
        if (status == 'actif'):
            self.list[id][1] = curses.color_pair(2)
        elif (status == 'away' or status == 'idle' or status == 'lock'):
            self.list[id][1] = curses.color_pair(3)
        elif (status == 'logout'):
            self.list[id][1] = curses.color_pair(4)
        else:
            self.list[id][1] = curses.color_pair(5)
        if (self.list[id][2] == 0):
            self.pstr(id, self.getBuddyName(id))
        else:
            self.pstr(id, self.getBuddyName(id), curses.A_BLINK | curses.A_REVERSE | curses.A_BOLD)

    def isSelected(self, i):
        for s in self.selected:
            if (s == i):
                return (True)
        return (False)

    def pstr(self, i, text, flags = curses.A_BOLD):
        try:
            self.frame.addstr(i, 0, text, self.getBuddyState(i) | flags)
        except:
            return

    def refresh(self):

        self.frame.refresh(self.iscroll, 0, self.y, self.x, self.h+self.y-1, self.x+self.w)

    def wrefresh(self):
        i = 0
        for buddy, state, havemsg in self.list:
            self.pstr(i, buddy)
            i += 1
        self.refresh()

    def getBuddyId(self, login):
        i = 0
        for buddy, state, havemsg in self.list:
            if (buddy == login):
                return (i)
            i += 1
        return (-1)
