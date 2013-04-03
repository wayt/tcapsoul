##
##
##
##
##

import          tcapsoulAPI as tcsapi
import          ns
import          socket
import          imp
import          thread
import          traceback
import          random
import          time

SOCK_STREAM             = socket.SOCK_STREAM
SOCK_DGRAM              = socket.SOCK_DGRAM

SOCK_CLOSE              = '\x02'
SOCK_SEND               = '\x01'
SOCK_SEARCH             = '\x08'
SOCK_BIND               = '\x09'

SOCKTCP_SEND            = '\x0A'
SOCKTCP_SENDCHECKSUM    = '\x03'
SOCKTCP_CHECKSUM        = '\x04'
SOCKTCP_CONNECT         = '\x05'
SOCKTCP_ACCEPT          = '\x06'
SOCKTCP_CLOSE           = '\x0B'

STOP_BRATE              = 0.01

class           tcapsoulSocket(ns.ns_connection):

    def         __init__(self, sockType):
        ns.ns_connection.__init__(self)
        conf = self.loadModule('/etc/tcapsoul/tcapsoul.conf')
        self.login = conf.login
        self.password = conf.password
        self.__RECV = dict()
        self.sockType = sockType
        if (self.sockType == SOCK_DGRAM):
            self.startSocket('TMPUDP-%s' % random.random(), 'SOCKTYPE=UDP')

    def         startSocket(self, id, value):
        self.location = id
        self.nsclient = value
        self.connectToNsServer(0)
        self.auth(self.login, self.password)
        #thread.start_new_thread(self.__loopSocket, tuple())

    def         calcCheckSum(self, data):
        total = 0
        for byte in data:
            total += ord(byte)
        return ("%d"%total)
            
    def         __dataParser(self, client, data):
        id = data[0:1]
        data = data[1:]

        if (id == '\x01'):
            client.rawdatas += data
            self.sendMsgToPort(client.port, self.calcCheckSum(data))
        elif (id == '\x02'):
            client.isConnected = False
            self.__RECV.pop(client.id)
        elif (id == '\x03' and client.lastSendCheckSum == data):
            client.sendMsgToPort(client.port, '\x04')
        elif (id == '\x04'):
            client.dataStack += client.rawdatas
            client.rawdatas = ''

                
    def         waitTrameId(self, id, port = -1):
        while 1:
            trame = self.waitTrame()
            if (port != -1 and trame.fromPort != port):
                continue
            if (trame.type == ns.TRAMTYPE_MSG and trame.msg[0:1] == id):
                trame.msg = trame.msg[1:]
                return (trame)
        return ('')
#########
    def         pstr(self, text):
        print text

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


    def         linkConnection(self, trame):
        b = tcsapi.BuddyObject(trame.fromName)
        b.port = trame.fromPort
        #b.location = trame.location
        #b.nsclient = trame.nsclient
        b.ip = trame.fromIp
        return (b)

    def         checkSum(self, t):

        res = 0
        i = 0
        while (i < len(t)):
            res += ord(t[i:i+1])
            i += 1
        return ("%s" % res)

##### Socket abstract

    def         connect(self, login, portId):
        self.startSocket("CONNECT-%s:%s" % (login, portId), "TCS_SOCKETWRAPPER=%s" % self.sockType)

        self.bindLogin(login)
        port = ''
        while 1:
            trame = self.waitTrame()
            if ((trame.type == ns.TRAMTYPE_WHO or trame.type == ns.TRAMTYPE_CHANGESTATE) and trame.location == 'BIND-%s' % portId):
                break
        self.sendMsgToPort(trame.fromPort, "%s%s" % (SOCKTCP_CONNECT, portId))
        trame = self.waitTrameId(SOCKTCP_ACCEPT)
        self.__link = self.linkConnection(trame)
        return (0)


    def         bind(self, portId):
        self.startSocket("BIND-%s" % portId, "TCS_SOCKETWRAPPER=%s" % self.sockType)
        return (0)

    def         accept(self):
        while 1:
            trame = self.waitTrameId(SOCKTCP_CONNECT)
            print 'RECV CONNECT : "BIND-%s" By %s' % (trame.msg, trame.fromPort)
            print 'BIND CONNECT : "%s"' % self.location
            if ('BIND-%s' % trame.msg == self.location):
                break
        magicPort = "TCP_CTLWRAPPER=%s"%random.random()
        newsock = tcapsoulSocket('TCP')
        newsock.bind(magicPort)
        newsock.sendMsgToPort(trame.fromPort, "%s%s" % (SOCKTCP_ACCEPT, magicPort))
        newsock.__link = self.linkConnection(trame)
        return ([newsock.__link.port, newsock.__link.name], newsock)

    def         close(self):
        if (self.sockType == 'TCP'):
            self.sendMsgToPort(self.__link, SOCKTCP_CLOSE)
        return (0)


    def         send(self, data):

        #if (len(data) > 4096):
        #    return (-1)
        csok = True
        buffer = ''
        while (len(data) != 0 or buffer != ''):
            if (csok == True):
                buffer = data[0:1200]
                data = data[1200:]
            cs = self.checkSum(buffer)
            self.sendMsgToPort(self.__link.port, "%s%s" % (SOCKTCP_SEND, buffer))
            time.sleep(STOP_BRATE)
            return (0)

    def         recv(self, len = 0):
        
        while 1:
            trame = self.waitTrameId(SOCKTCP_SEND)
            if (trame.msg == SOCKTCP_CLOSE):
                return ('')
            buffer = trame.msg
            return (buffer)            

    def         recvfrom(self, len = 0):
        while 1:
            trame = self.waitTrame()
            if (trame.type == ns.TRAMTYPE_MSG):
                return ([trame.fromPort, trame.location, trame.fromName], trame.msg)

    def         sendto(self, addr, data):
        self.pstr('SEND TO %s : "%s"' % (addr[0], data))
        self.sendMsgToPort(addr[0], data)

if (__name__ == '__main__'):
    import os
    import time

    PORT_BIND = 'test'
    MESSAGE = 'COUCOU'

    pid = os.fork()
    if (pid == 0):
        tcss = tcapsoulSocket(SOCK_STREAM)
        print 'Server is connected'
        print 'SERVER[BIND] : %s' % tcss.bind(PORT_BIND)
        addr, new = tcss.accept()
        print 'SERVER[ACCEPT] : new user : %s@%s' % (addr[0], addr[1])
        while 1:
            msg = new.recv(4096)
            print 'SERVER[RECV] : %s@%s -> "%s"' % (addr[0], addr[1], msg)
    else:
        tcss = tcapsoulSocket(SOCK_STREAM)
        print 'CLIENT is connected TO NS-SERVER'
        print '----->>>>---->CLIENT[CONNECT] : %s' % tcss.connect(tcss.login, PORT_BIND)
        print 'CLIENT[CONNECTED]'
        while 1:
            tcss.send(MESSAGE)
            print 'CLIENT[SEND(%s, %s) -> "%s"' % (tcss.login, PORT_BIND, MESSAGE)
            time.sleep(1)
