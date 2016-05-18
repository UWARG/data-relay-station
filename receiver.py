### receiver.py

import serial
import struct
from xbee.zigbee import ZigBee
from sys import platform as _platform
import time

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

    def __init__(self, db_type):
        self.data_shape = {key:struct.Struct(
            ''.join(map(lambda x: x[0], packet))) for key, packet in db_type.iteritems()}

        #Print out packet size
        for key, packet in self.data_shape.iteritems():
            print("Packet Size {}: {}".format(key,packet.size))
        
        #Check if all packets have the same size
        self.data_size = self.data_shape[self.data_shape.keys()[0]].size
        for i in xrange(1,len(self.data_shape)):
            if (self.data_shape[i].size != self.data_size):
                print("Data Packets are not the same in size: " + str(self.data_size) + " " + str(self.data_shape[i].size))
        
        self.expected_packets = self.data_size / MAX_PACKET_SIZE + 1
        self.source_addr = None
        self.source_addr_long = None
        self.packet_type = None
        self.outbound = []
        self.rssi = -100
        self.stored_data = [tuple([None])]*len(self.data_shape.keys())

    def async_tx(self, command):
        """Eventually send a command
        """
        self.outbound.append(command)



    def connect_to_xbee(self):

        #detect platform and format port names
        if _platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif _platform.startswith('linux'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        else:
            raise EnvironmentError('Unsupported platform: ' + _platform)



        #search for available ports
        self.port_to_connect = ''
        self.timeout_start_time = time.time()
        while self.port_to_connect == '': 
            self.ports_avail = []
            if (time.time() - self.timeout_start_time)>100:
                raise EnvironmentError('Timed out searching for serial connection.')
            
            #loop through all possible ports and try to connect
            for port in ports:
                try:
                    s = serial.Serial(port)
                    s.close()
                    self.ports_avail.append(port)
                except (OSError, serial.SerialException):
                    pass
            #Check the right number of Serial ports are connected        
            if len(self.ports_avail) ==1:
                self.port_to_connect = self.ports_avail[0]
                
            elif len(self.ports_avail)==0:
                #No Serial port found, continue looping.
                print "No serial port detected. Trying again..."
                time.sleep(1)

            elif len(self.ports_avail)>1:
                #Multiple serial ports detected. Get user input to decide which one to connect to
                com_input = raw_input("Multiple serial ports available. Which serial port do you want? \n"+str(self.ports_avail)).upper();
                if com_input in self.ports_avail:
                    self.port_to_connect = com_input

        #connect to xbee
        self.xbee = ZigBee(serial.Serial(self.port_to_connect, 115200))
        print 'xbee created/initialized'
        return self




    def data_lines(self):

        #counter to limit extra packets sent
        packetCnt=0
        while True:
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
                    #else:
                        #self.stored_data[data_type] += tuple([None] * len([i for i in data_shape.format if i != 'x']))
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
                print "sent a command"
            self.outbound = []


    def __enter__(self):
        self.connect_to_xbee()

    def __exit__(self, type, value, traceback):
        self.xbee = None
        self.ser.close()
        if isinstance(value, serial.SerialException):
            print traceback
            return True
