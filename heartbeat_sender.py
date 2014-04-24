import socket
import time
import sys

serverAddress = ("localhost", 1234)
#s = socket.socket()

try:
        s = socket.create_connection(serverAddress)
#        s.connect(serverAddress)
except:
        print 'Unable to connect'
        sys.exit()
s.send("commander")
while True:
        s.send("YO")
        print 'Message sent successfully'
        time.sleep(1)
        print 'Sending...'

s.close()
