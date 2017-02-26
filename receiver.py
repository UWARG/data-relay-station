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


class Receiver:

    def __init__(self, db_type, serialport, consumer):
        self.data_shape = {key:struct.Struct(
            ''.join(map(lambda x: x[0], packet))) for key, packet in db_type.iteritems()}
        self.consumer = consumer
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

        self.xbee = ZigBee(serial.Serial(serialport, 115200), callback=self.data_lines)
        print 'saved xbee' , self.xbee

    def async_tx(self, command):
        """Eventually send a command
        """
        self.outbound.append(command)
    def write_telem(self, packet):
        self.consumer.write(str(packet).replace("None", "") + "\r\n")

    def data_lines(self, packet):

        payload = ''
        yield_data = ()

        if packet.get('id', None) != 'rx':
            #Checks for tx_response
            if packet.get('id', None) == 'tx_status':
                print('got tx_status frame')
            #Checks for command response and signal strength
            elif packet.get('id', None) == 'at_response':
                if packet.get('command', None) == 'DB':
                    self.rssi = ord(packet.get('parameter',self.rssi))
        else:
            self.source_addr_long = packet.get(
                    'source_addr_long')
            self.source_addr = packet.get(
                    'source_addr')

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

            self.write_telem(yield_data)



        # flush the command queue to the xbee
        for cmd in self.outbound:
            self.xbee.tx(dest_addr_long=self.source_addr_long,
                    dest_addr=self.source_addr, data=cmd)
            print("command {}".format(' '.join("0x{:02x}".format(i) for i in cmd)))
            print("sent a command")
        self.outbound = []


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
