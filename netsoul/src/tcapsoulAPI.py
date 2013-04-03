#######
######
######
#####   TCAPSOUL API
###
##
#


### Method to call for tcapsoul API :

###     -loadconfig() << Load tcapsoul configuration file
###     -connect() << Connection to ns-server
###     -sendTo(buddyObj, text)         <<
###     -sendToLogin(login, text)       <<
###     -changeStatus(TCSSTATUS)        <<
###     -addBuddy(buddyname)


#####
##### HANDLES : You must have this method on your object
###
###
###     -buddySendMessage(buddy, message)
###     -buddyChangeStatus(buddy, TCSSTATUS)

### ERROR LIST ON TCAPSOUL

TCSERR_UNKNOW = 0
TCSERR_CONFIGFILE = 1
TCSERR_CONNECTION = 2
TCSERR_TRAMENOTBUDDY = 3

### STATUS ON TCAPSOUL
TCSSTATUS_ACTIF = 'actif'
TCSSTATUS_AWAY = 'away'
TCSSTATUS_LOCK = 'lock'
TCSSTATUS_LOGIN = 'login'
TCSSTATUS_LOGOUT = 'logout'
TCSSTATUS_OFFLINE = TCSSTATUS_LOGOUT

import ns
import imp
import thread
import time
import traceback

class           BuddyObject:

    def         __init__(self, name):
        self.name = name
        self.ip = 'Offline'
        self.port = 4242
        self.location = 'no location'
        self.nsclient = 'no ns client'
        self.status = TCSSTATUS_LOGOUT

    def         isConnected(self):
        if (self.status == TCSSTATUS_LOGOUT):
            return (False)
        return (True)

class           TcapsoulException(Exception):

    def         __init__(self, message, errorId = TCSERR_UNKNOW):

        Exception.__init__(self, message)
        self.errormessage = message
        self.errorId = errorId


####                              #####
####            The Tcapsoul API  #####
####                              #####
####                              #####


class           TcapsoulAPI(ns.ns_connection):

    #### API PUBLIC METHOD ####

    def         start(self):
        self.sendSysInfo('STARTING TCAPSOUL-API V0.1...')
        thread.start_new_thread(self.connection, (0, 0))

    def         addBuddy(self, buddyname, flush=True):

        self.buddyList[buddyname] = list([BuddyObject(buddyname)])
        self.buddyList[buddyname][0].state = TCSSTATUS_OFFLINE
        self.buddyChangeStatus(self.buddyList[buddyname][0])
        if (flush == True):
            self.bindLogin(buddyname)

    def         connection(self, ip = ns.DEFAULT_NSSERVER, a = 0):
        self.connectToNsServer(0)
        self.auth(self.login, self.password)
        self.sendSysInfo('You are connected')
        self.bindLoginList(self.conf.buddys)
        self.sendState('actif')
        self.__loop()

    def         changeStatus(self, status):
        self.sendState(status)

    ### Use it only for one nsclient ###
    def         sendToBuddy(self, buddyObj, text):
        self.sendMsgToUser(buddyObj, text)
        return (0)

    ### Use it for multiple location too ###
    def         sendToLogin(self, login, text):
        self.sendMsg(login, text)
        return (0)

    def         loop(self):
        try:
            while 1:
                trame = self.waitTrame()
                try:
                    buddy = self.getBuddyFromTrame(trame)
                except TcapsoulException as e:
                    if (e.errorId == TCSERR_TRAMENOTBUDDY):
                        self.sendSysInfo('TcapsoulAPI-WARNING : %s' % e.errormessage)
                        continue
                    raise e
                if (trame.type == ns.TRAMTYPE_MSG):
                    self.buddySendMessage(buddy, trame.msg)
                elif (trame.type == ns.TRAMTYPE_CHANGESTATE or trame.type == ns.TRAMTYPE_WHO):
                    self.__changeBuddyState(trame)
                    self.buddyChangeStatus(buddy)
        except:
            self.sendSysInfo('TCAPSOUL API HAS CRASH ! :\'(')
            self.sendSysInfo(traceback.format_exc())

    ### For API AND EXTENTIONS ####

    def         __init__(self, sysinfo):        
        ns.ns_connection.__init__(self)
        self.pstr = sysinfo
        self.buddyList = dict()
        self.loadConfig()
        self.__APIconnected = False

    def         __loop(self, a = 0, b = 0):
        self.loop()

    def         __getPassword(self, conf):
        self.password = conf.password

    def         loadModule(self, file):
        try:
            fp = open(file, 'U')
        except:
            raise TcapsoulException("Module %s not exist" % file)
        description = ('.py', 'U', 1)
        name = 'tcapsoul_conf'
        try:
            return (imp.load_module(name, fp, file, description))
        finally:
            if fp:
                fp.close()


    def         loadConfig(self, file = '/etc/tcapsoul/tcapsoul.conf'):
        try:
            self.conf = self.loadModule(file)
        except TcapsoulException:
            try:
                self.sendSysInfo('Configuration file not found try in local ./tcapsoul.conf')
                self.conf = self.loadModule('./tcapsoul.conf')
            except:
                raise TcapsoulException("Tcapsoul configuration file not found at ./tcapsoul.conf")
        for buddyname in self.conf.buddys:
            self.addBuddy(buddyname, flush=False)
        
        self.__getPassword(self.conf)
        if (hasattr(self.conf, 'login') != False):
            self.login = self.conf.login
        else:
            self.login = self.readline('Login:')
        if (hasattr(self.conf, 'nsclient') != False):
            self.nsclient = self.conf.nsclient
        else:
            self.nsclient = 'tcapsoul-%s' % conf.TCAPSOUL_VERSION
        if (hasattr(self.conf, 'location') != False):
            self.location = self.conf.location
        else:
            self.location = 'dtc'

    def         getBuddyFromTrame(self, trame):
        if (hasattr(trame, 'fromName') == 0):
            raise TcapsoulException('Not a BuddyTrame', TCSERR_TRAMENOTBUDDY)
        for name, multipleLocation in self.buddyList.iteritems():
            for buddy in multipleLocation:
                #if (buddy.name == trame.fromName and buddy.port == trame.fromPort and buddy.ip == trame.fromIp): --> Gestion multicomptes
                if (buddy.name == trame.fromName):
                    return (buddy)

        # Else if buddy not exist
        newBuddy = BuddyObject(trame.fromName)
        self.__changeBuddyState(trame, newBuddy)
        for name in self.buddyList:
            if (name == trame.fromName):
                self.buddyList[name].append(newBuddy)
                return (newBuddy)
        self.buddyList[newBuddy.name] = list([newBuddy])
        return (newBuddy)

    def         __changeBuddyState(self, trame, buddy = 0):
            
        if (buddy == 0):
            buddy = self.getBuddyFromTrame(trame)
        buddy.state = trame.state
        buddy.location = trame.location
        buddy.ip = trame.fromIp
        buddy.port = trame.fromPort
        buddy.nsclient = trame.client
        buddy.location = trame.location


class           tcapsoulAPItest(TcapsoulAPI):

    def         __init__(self):
        
        TcapsoulAPI.__init__(self, self.pstr)

    def         pstr(self, text):
        print "SYSINFO : '%s'" % text

    
    def         buddySendMessage(self, buddy, msg):
        print "BUDDY %s SAY : %s" % (buddy.name, msg)


    def         buddyChangeStatus(self, buddy):
        print "BUDDY %s STATUS : %s" % (buddy.name, buddy.state)

    def         sendSysInfo(self, text):
        print 'Sys info : ', text

if __name__ == "__main__":
    import time

    a = tcapsoulAPItest()
    a.start()
    time.sleep(2)
    print 'TCAPSOUL EXEMPLE TEST STARTING'
    a.sendState('actif')
    while 1:
        buffer = raw_input(">>>")
        i = buffer.find(' ')
        usr = buffer[:i]
        msg = buffer[i+1:]
        a.sendToLogin(usr, msg)
