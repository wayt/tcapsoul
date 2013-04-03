
import socket, sys, os, hashlib, time, urllib

#10.42.1.59 interne
#ns-server.epita.fr externe -> route 10.42.1.59 at school

#DEFAULT_NSSERVER = ("ns-server.epita.fr", 4242)
DEFAULT_NSSERVER = ("10.42.1.59", 4242)
TRAMTYPE_MSG = 0
TRAMTYPE_USERTYPING = 1
TRAMTYPE_USERCANCELTYPING = 2
TRAMTYPE_CHANGESTATE = 3
TRAMTYPE_NONE = 4
TRAMTYPE_WHO = 5

class           trameObj:

     def        __init__(self):
          self.type = 0
          self.msg = ''
          self.fromPort = 0
          self.fromName = ''
          self.state = ''
          self.fromIp = ''

class           ns_connection:

     def        __init__(self, addr = DEFAULT_NSSERVER, location = 'Sauce', nsclient = "white%20windows%20klk"):

          self.addr = addr
          self.location = location
          self.nsclient = nsclient
          self.pstr = self.defaultpstr
          self._srbuffer = ''

     def        defaultpstr(self, txt):
          print txt

     def        connectToNsServer(self, maxtentative = 1):

          nbtentative = 0
          self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          while 1:
               try:
                    self.pstr("Tentative %d, connect to %s" % (nbtentative, self.addr))
                    self.sock.connect(self.addr)
                    return (0)
               except:
                    nbtentative += 1
                    if (maxtentative != 0 and nbtentative > maxtentative):
                         self.pstr("Echec...")
                         return (-1)
                    else:
                         self.pstr("Impossible de se connecter, retry")
                         time.sleep(1)


     def        auth(self, login, password):

          #self.pstr('LOGIN=%s PASSWORD=%s' % (login, password))
          Mess = self.sock.recv(4096)
          TrameAuth = Mess.split(' ')
          Hash = TrameAuth[2]
          ip = TrameAuth[3]
          port = TrameAuth[4]
          time_stamp_serv = int(TrameAuth[5])

          self.sock.send("auth_ag ext_user none none" + '\n')
          Mess = self.sock.recv(4096)
          TrameAuth = Mess.split(' -- ')
          if (TrameAuth[0] != "rep 002"):
               return (-1)
          HashBack = hashlib.md5("%s-%s/%s%s" % (Hash, ip, port, password)).hexdigest()
          self.pstr("AUTH: SEND 'ext_user_log '%s' '%s' '%s' '%s''" % (login, HashBack, self.location, self.nsclient))
          self.sock.send("ext_user_log %s %s %s %s\n" % (login, HashBack, self.location, self.nsclient))
          Mess = self.sock.recv(4096)
          TrameAuth = Mess.split(' -- ')
          if (TrameAuth[0] != "rep 002"):
               return (-1)
          return (0)

     def        saveBuddyList(self, file, buddy):
          fdw = open(file, 'wc')
          fdr = open(file, 'rb')
          lines = fdr.readlines()
          fdr.close()
          i = 0
          while (i < len(lines)):
               if (lines[i].find('buddys=[') != -1):
                    e = lines[i].rfind("']")
                    lines[i] = lines[i][:e-2] + buddy + "']"
               i += 1
          fdw.write(lines.join('\n'))
          fdw.close()
          return (0)

     def        sendReq(self, req):
          self.sock.send("%s\n" % req)


     def        sendState(self, state):

          t = int(time.time())
          self.pstr("user_cmd state '%s:%d'" % (state, t))
          self.sock.send("state %s:%d\n" % (state, t))


     def        sendMsg(self, login, msg):
          msg = urllib.quote(msg).replace('/', '%2F')
          self.sendReq("user_cmd msg_user %s msg %s" % (login, msg))

     def        sendMsgList(self, loginList, msg):

          total = '{'
          for login in loginList:
               total = total + login + ','
          total = total[:len(total)-1] + '}'
          
          msg = urllib.quote(msg).replace('/', '%2F')
          self.sendReq("user_cmd msg_user %s msg %s" % (total, msg))
     

     def        sendMsgToUser(self, User, msg):
          msg = urllib.quote(msg)
          msg = msg.replace('/', '%2F')
          self.sendReq("user_cmd msg_user :%s msg %s" % (User.port, msg))

     def        sendMsgToPort(self, port, msg):
          msg = urllib.quote(msg)
          msg = msg.replace('/', '%2F')
          self.sendReq("user_cmd msg_user :%s msg %s" % (port, msg))


     def        recvNsTrame(self):
          while (self._srbuffer.find('\n') == -1):
               tmp = self.sock.recv(16384)
               if (tmp == ''):
                    print 'NS-SERVER CUT ME'
                    exit(0)
               self._srbuffer += tmp
          i = self._srbuffer.find('\n')
          result = self._srbuffer[:i]
          self._srbuffer = self._srbuffer[i+1:]
          return (result)
     
     def        bindLogin(self, login):
          self.sendReq("user_cmd watch_log_user %s" % login)
          self.whoLogin(login)

     def        whoLogin(self, login):
          self.sendReq("user_cmd who %s" % login)

     def        bindLoginList(self, list):
          buddys = '{'
          for buddy in list:
               buddys = buddys + buddy + ','
          buddys = buddys[:len(buddys)-1]
          buddys += '}'
          self.sendReq("user_cmd watch_log_user %s" % buddys)
          self.sendReq("user_cmd who %s" % buddys)

     def        bindUser(self, User):
          self.sendReq("user_cmd watch_log_user :%d" % User.port)
          self.sendReq("user_cmd who :%d" % User.port)

     def        makeUserCmdObj(self, ucHead):

          #ucHead = reponse[9:].split(' | ')
          ucInfo = ucHead[0].split(':')
          ucMess = ucHead[1].split(' ')
          res = trameObj
          nameip = ucInfo[3].split('@')
          res.fromName = nameip[0]
          res.fromIp = nameip[1]
          res.fromPort = ucInfo[1]
          res.location = ucInfo[5]
          #res.client = ucHead[]

          if (ucMess[0] == 'msg'):
               first_taping = 0
               message = urllib.unquote(ucMess[1])
               res.type = TRAMTYPE_MSG
               res.msg = message
               res.fromPort = ucInfo[0].split(' ')[1]
          elif (ucMess[0] == 'dotnetSoul_UserTyping'):
               res.type = TRAMTYPE_USERTYPING
          elif (ucMess[0] == 'dotnetSoul_UsercancelledTyping'):
               res.type = TRAMTYPE_USERCANCELTYPING
          elif (ucMess[0] == 'login'):
               res.type = TRAMTYPE_CHANGESTATE
               res.state = 'login'
          elif (ucMess[0] == 'logout'):
               res.type = TRAMTYPE_CHANGESTATE
               res.state = 'logout'
          elif (ucMess[0] == 'state'):
               res.type = TRAMTYPE_CHANGESTATE
               res.state = ucMess[1].split(':')[0]
          elif (ucMess[0] == 'who' and ucHead[1] != 'who rep 002 -- cmd end'):
               res.fromPort = ucMess[1]
               res.fromName = ucMess[2]
               res.fromIp = ucMess[3]
               if (len(ucMess) > 9):
                    res.location = urllib.unquote(ucMess[9])
               else:
                    res.location = '???'
               if (len(ucMess) > 11):
                    res.state = ucMess[11].split(':')[0]
               else:
                    res.state = '???'
               if (len(ucMess) > 12):
                    res.client = urllib.unquote(ucMess[12])
               else:
                    res.client = '???'
               res.type = TRAMTYPE_WHO
          else:
               res.type = TRAMTYPE_NONE
          return (res)

     def        makeTrameObj(self, reponse):

          if (reponse[0:8] == 'user_cmd'):
               return (self.makeUserCmdObj(reponse.split(' | ')))
          elif (reponse[0:4] == "ping"):
               self.pstr("RECV PING FROM SERVER")
               self.sock.send(reponse)
          else:
               self.pstr("[RAW_NS_MESSAGE] : '%s'" % reponse)
          res = trameObj
          res.type = TRAMTYPE_NONE
          res.msg = reponse
          return (res)

     def        waitTrame(self):
          trame = self.recvNsTrame()
          return (self.makeTrameObj(trame))

     def        closeNsConn(self):
          self.sock.close()
