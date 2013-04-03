
import curses
import time
import thread
import os

class battery:

    def         __init__(self, battfile = ''):
        self.battpath = battfile
        self.used = 0
        if (self.battpath == ''):
            self.battpath = self.find_battery()

    def     find_battery(self):
        files = os.listdir("/proc/acpi/battery")
        for dir in files:
            fd = open("/proc/acpi/battery/%s/info" % dir, 'r')
            lines = fd.readlines()
            fd.close()
            if (lines[0].find("yes") != -1):
                return ("/proc/acpi/battery/%s" % dir)
        return ("")

    def     get_int(self, string):
        res = ""
        for c in string:
            if (c >= '0' and c <= '9'):
                res = res + c
            if (res == ""):
                res = "0"
        return (int(res))

    def     refresh(self):

        fd_info = open("%s/info" % self.battpath)
        fd_state = open("%s/state" % self.battpath)
        self.cap = fd_info.readlines()
        self.info = fd_state.readlines()
        fd_info.close()
        fd_state.close()
        return (0)

    def             calc_purcent(self):
        
        rcap = get_int(self.info[4])
        maxcap = get_int(self.cap[1])
        return (int(float(float(rcap) / float(maxcap)) * 100))

    def             calc_time(self):

        rcap = int(self.info[4].replace("remaining capacity:", "").replace("mAh", ""))
        prate = int(self.info[3].replace("present rate:", "").replace("mA", ""))
        if (prate == 0):
            return ("AC")
        elif (self.info[2].find("charging\n") != -1 and self.info[2].find("discharging") == -1):
            return ("Charging")
        res = ""
        tmp = float((float(rcap) / float(prate)) * 3600)
        res = "%dh%dm" % (int(tmp / 3600), int(tmp / 60) % 60)
        return (res)

    def             getsource(self):

        battstate = self.info[2]
        if (battstate.find("charged") != -1):
            return ("AC")
        return ("DC")

    def             getstrstate(self):

        self.refresh()
        if (self.getsource() == 'AC'):
            return ('AC MODE')
        return (self.calc_time())


class   InfoBar:

    def __init__(self, root):

        self.root = root
        self.user = ''
        self.used = False
        if (os.path.exists('/proc/acpi/battery/') == True):
            self.acpi = True
            self.batt = battery()
        else:
            self.capi = False
        thread.start_new_thread(self.infos, (0, 0))

    def currentBuddy(self, buddy):
        #try:
        self.user = "%s at %s on %s@%s:%s" % (buddy.name, buddy.location, buddy.nsclient, buddy.ip, buddy.port)
        #except:
        #    self.user = buddy

    def infos(self, a, b):
        while 1:
            self.mutex(True)
            self.refresh()
            self.mutex(False)
            time.sleep(1)

    def make(self, h, w, y, x):
        self.h = h
        self.w = w
        self.y = y
        self.x = x
        self.frame = curses.newpad(h, 512)
        self.refresh()

    def mutex(self, bool):
        if (bool == True):
            while self.used == True:
                time.sleep(0.0001)
            self.used = True
        else:
            self.used = False

    def refresh(self):

        # if (self.acpi == True):
        #     self.frame.addstr(0, 0, "%s - Battery:%s - %s" % (time.ctime(), self.batt.getstrstate(), self.user))
        # else:
        #     self.frame.addstr(0, 0, "%s - %s" % (time.ctime(), self.user))
        self.frame.clrtoeol()
        self.frame.refresh(0, 0, self.y, self.x, self.h, self.w-1)
        self.used = 0
