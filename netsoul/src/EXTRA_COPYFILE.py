#!/usr/bin/python
##
##
##
##
##
##

import tcapsoulSocket as tcss
import sys
import os
import time

FILENAME='\x01'
DATAS='\x02'
END='\x03'

# \x01=FILENAME
# \x02=DATAS
# \x03=END

def     pstr(text):
    print text


ARGV = sys.argv
PSTR = pstr

def     pusage():
    PSTR( 'USAGE : ./EXTRA_COPYFILE s|c path|login [login|]')
    PSTR( '\t- s = People Who send file : ./COPY s fileToSend loginWhoRecveive')
    PSTR( '\t- c = Who recveive the file : ./COPY c loginWhoSend')


def     start():

    if (len(ARGV) == 1):
        pusage()
        return (0)

    if (ARGV[1] == 'c' and len(ARGV) == 3):
            sock = tcss.tcapsoulSocket(tcss.SOCK_STREAM)
            sock.bind('TCSS-CP-%s' % ARGV[2])
            while 1:
                addr, new = sock.accept()
                if (addr[1] == ARGV[2]):
                    break
                PSTR( '%s has try to get your file!' % addr[1])

            while 1:
                buffer = new.recv(4096)
                if (buffer == ''):
                    PSTR( 'Connection closed by server')
                    break
                if (buffer[0:1] == FILENAME):
                    filename = buffer[1:]
                    PSTR( 'FILE NAME : %s' % filename)
                    fd = open(filename, 'wcb')
                elif (buffer[0:1] == DATAS):
                    fd.write(buffer[1:])
                elif (buffer[0:1] == END):
                    PSTR( 'END')
                    break
                else:
                    PSTR('DO NOT KNOW command=%s' % ord(buffer[0:1]))
            fd.close()
            new.close()
            sock.close()
            PSTR( 'END !')

    elif (ARGV[1] == 's' and len(ARGV) == 4):
        sock = tcss.tcapsoulSocket(tcss.SOCK_STREAM)
        sock.connect(ARGV[3], 'TCSS-CP-%s' % sock.login)
        sock.send("%s%s" % (FILENAME, ARGV[2][ARGV[2].rfind('/')+1:]))
        size = os.stat(ARGV[2]).st_size

        fd = open(ARGV[2], 'rb')
        i = 0
        sav = int(time.time())
        diff = 0
        while (1):
            buffer = fd.read(1024)
            i += len(buffer)
            if (buffer == ''):
                break
            sock.send("%s%s" % (DATAS, buffer))
            cur = int(time.time())
            if (cur != sav):
                os.write(1, 'SEND AT %sKo/s - %s%% Transfered...\r' % (float(i-diff) / 1000, int((float(i) / float(size))*100)))
                sav = cur
                diff = i
        sock.send(END)
        fd.close()
        sock.close()
    else:
        pusage()
