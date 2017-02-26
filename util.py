import serial.tools.list_ports
import os, errno

def detect_xbee_ports():
    xbee_ports=[]
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if('FTDIBUS' in port[2]):
            xbee_ports.append(port[0])
    return xbee_ports

def create_directory(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        #Catch and ignore error of directory already existing
        if exception.errno != errno.EEXIST:
            raise
