import serial.tools.list_ports

def detect_xbee_ports():
    xbee_ports=[]
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if('FTDIBUS' in port[2]):
            xbee_ports.append(port[0])
    return xbee_ports
