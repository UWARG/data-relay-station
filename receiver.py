### receiver.py

import serial
import struct
from xbee.zigbee import ZigBee
from sys import platform as _platform
import time
import glob
import os,errno

# The max allowed size for an api packet
MAX_PACKET_SIZE = 100


class WriteToFileMiddleware:
    """Take a generator, write each element out to file and
    forward it
    """
    def __init__(self, gen, filename, header):
        print('initing {}'.format(self.__class__))
        self.gen = gen
        self.filename = filename
        self.header = header

        #Create folder if not already there
        if not os.path.exists(os.path.dirname(self.filename)):
            try:
                os.makedirs(os.path.dirname(self.filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        #self.transport = gen.transport

    def data_lines(self):
        # write header line out to file

        print('writing headers')
        with open(self.filename, 'w') as outfile:
            outfile.write("{}\r\n".format(self.header))

        for line in self.gen.data_lines():
            # write element to file
            with open(self.filename, 'a') as outfile:
                outfile.write(str(line).replace('(','').replace(')','').replace('None','') + '\n')
            # re-yield element
            yield line


class Receiver:

    def __init__(self, db_type, serialport):
        self.data_shape = {key:struct.Struct(
            ''.join(map(lambda x: x[0], packet))) for key, packet in db_type.iteritems()}

        #Print out packet size
        for key, packet in self.data_shape.iteritems():
            print("Packet Size {}: {}".format(key,packet.size))

        #Check if all packets have the same size
        self.data_size = self.data_shape[self.data_shape.keys()[0]].size
        data_mismatch = False
        for i in xrange(1,len(self.data_shape)):
            if (self.data_shape[i].size != self.data_size):
                print("Data Packets are not the same in size: " + str(self.data_size) + " " + str(self.data_shape[i].size))
                data_mismatch = True
        if data_mismatch:
            raise ValueError("Data packet size mismatch")

        self.expected_packets = self.data_size / MAX_PACKET_SIZE + 1
        self.source_addr = None
        self.source_addr_long = None
        self.packet_type = None
        self.outbound = []
        self.rssi = -100
        self.stored_data = [tuple([None])]*len(self.data_shape.keys())

        self.xbee = ZigBee(serial.Serial(serialport, 115200))

    def async_tx(self, command):
        """Eventually send a command
        """
        self.outbound.append(command)


    def reconnect_xbee(self):
    #search for available ports
        port_to_connect = ''
        while port_to_connect == '':

            #detect platform and format port names
            if _platform.startswith('win'):
                ports = ['COM%s' % (i + 1) for i in range(256)]
            elif _platform.startswith('linux'):
                # this excludes your current terminal "/dev/tty"
                ports = glob.glob('/dev/ttyUSB*')
            else:
                raise EnvironmentError('Unsupported platform: ' + _platform)

            ports_avail = []

            #loop through all possible ports and try to connect
            for port in ports:
                try:
                    s = serial.Serial(port)
                    s.close()
                    ports_avail.append(port)
                except (OSError, serial.SerialException):
                    pass

            if len(ports_avail) ==1:
                port_to_connect = ports_avail[0]

            elif len(ports_avail)==0:
                #No Serial port found, continue looping.
                print( "No serial port detected. Trying again...")
                time.sleep(1)

            elif len(ports_avail)>1:
                #Multiple serial ports detected. Get user input to decide which one to connect to
                #com_input = raw_input("Multiple serial ports available. Which serial port do you want? \n"+str(self.ports_avail)+":").upper();
                if self.default_serial == None:
                    raise EnvironmentError('Incorrect command line parameters. If there are multiple serial devices, indicate what port you want to be used using --serialport')
                elif self.default_serial.upper() in ports_avail:
                    port_to_connect = self.default_serial.upper()
                else:
                    raise EnvironmentError('Incorrect command line parameters. Serial port is not known as a valid port. Valid ports are:'+ str(ports_avail))

        #connect to xbee
        self.xbee = ZigBee(serial.Serial(port_to_connect, 115200))
        print('xbee connected to port ' + port_to_connect)
        return self


    def __enter__(self):
        return self


    def data_lines(self):

        #counter to limit extra packets sent
        packetCnt=0
        while True:
            try:
                payload = ''
                yield_data = ()
                for x in xrange(self.expected_packets):

                    packet = self.xbee.wait_read_frame()

                    #limit packets by only sending decibel strength only when if statement is true
                    if(packetCnt>=10):
                        self.xbee.at(command="DB")
                        packetCnt=0
                    packetCnt=packetCnt+1

                    while packet.get('id', None) != 'rx':
                        #Checks for tx_response
                        if packet.get('id', None) == 'tx_status':
                            print('got tx_status frame')
                        #Checks for command response and signal strength
                        elif packet.get('id', None) == 'at_response':
                            if packet.get('command', None) == 'DB':
                                self.rssi = ord(packet.get('parameter',self.rssi))
                        packet = self.xbee.wait_read_frame()

                    self.source_addr_long = packet.get(
                            'source_addr_long', self.source_addr_long)
                    self.source_addr = packet.get(
                            'source_addr', self.source_addr)

                    payload += packet['rf_data']

                    # Read first two bytes, to determine packet type
                    packet_type = struct.unpack("h", payload[:2])[0]

                    # Unpack Struct according to ID, and update global parameters
                    for data_type, data_shape in self.data_shape.iteritems():
                        if (packet_type == data_type):
                            self.stored_data[data_type] = data_shape.unpack(payload[2:])
                        else:
                            self.stored_data[data_type] = tuple([None] * len([i for i in data_shape.format if i != 'x']))
                    yield_data = tuple([i for j in self.stored_data for i in j])

                    #Add RSSI to each packet
                    yield_data += tuple([self.rssi])

                # let our data be processed - unpacks an array of tuples into one single tuple
                yield yield_data

                # flush the command queue to the xbee
                for cmd in self.outbound:
                    self.xbee.tx(dest_addr_long=self.source_addr_long,
                            dest_addr=self.source_addr, data=cmd)
                    print("command {}".format(' '.join("0x{:02x}".format(i) for i in cmd)))
                    print("sent a command")
                self.outbound = []
            except (OSError, serial.SerialException, IOError):
                #catch exception if xbee is unplugged, and try to reconnect
                print("Xbee disconnected!")
                #self.reconnect_xbee()


    def __exit__(self, type, value, traceback):
        print('exitting')
        self.xbee = None
        try:
            self.ser.close()
        except(AttributeError):
            #If the program exits before ser is initiallized, ser.close() will throw an AttributeError, which is caught and ignored
            pass
        if isinstance(value, serial.SerialException):
            print(traceback)
            return True
class ReceiverSimulator:
    def __init__(self, filename, speed):
        print('initing {}'.format(self.__class__))
        self._filename = filename
        self._speed = speed

    def data_lines(self):
        with open(self._filename, 'r') as infile:
            # skip the header line
            infile.next()
            for line in infile:
                #print 'yielding line'
                yield line
                time.sleep(self._speed)

    def async_tx(self, command):
        """Fake sending a command, since we obviously don't have anywhere
        to send it.
        """
        print("Noob is trying to send a command to a simulated plane LOL")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        print('printing traceback')
        print(traceback)
        print('end of traceback')
        pass
