import socket
import time
import sys

serverAddress = ("localhost", 1234)
heartbeatNum = 1
s = socket.socket()

try:
#        s = socket.create_connection(serverAddress)
        print "Waiting for connection...                  \r",
        s.connect(serverAddress)
except:
        print 'Unable to connect'
        sys.exit()
s.send("commander\r\n")
s.send("cancel_returnHome:0\r\n")
while True:
        s.send("send_heartbeat:0\r\n")
        print str(heartbeatNum) + (' Heartbeats' if heartbeatNum > 1 else ' Heartbeat') + ' sent successfully                              \r',
        heartbeatNum+=1
        time.sleep(10)
        print 'Sending...                                  \r',  

s.close()
