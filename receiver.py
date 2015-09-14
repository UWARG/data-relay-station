### receiver.py

import serial
import struct
from collections import defaultdict, deque
from xbee.zigbee import ZigBee
from sys import platform as _platform

from command import DEVICES

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
                outfile.write(str(line).replace('(','') + '\n')
            # re-yield element
            yield line


class Receiver:

    def __init__(self, db_type):
        self.data_shape = struct.Struct(
            ''.join(map(lambda x: x[0], db_type)))
        self.data_size = self.data_shape.size
        self.expected_packets = self.data_size / MAX_PACKET_SIZE + 1
        self.source_addr = None
        self.source_addr_long = None
        # If no device is given, it will be saved under None key, so legacy should still work
        self.outbound_queues = defaultdict(lambda: deque(maxlen = 100))

    def async_tx(self, command):
        """Eventually send a command
        """
        self.outbound_queues.get(command._target).append(command._command)

    def __enter__(self):
        if _platform == "linux" or _platform == "linux2":
            self.ser = serial.Serial('/dev/ttyUSB0', 38400)
        elif _platform == "win32":
            self.ser = serial.Serial('COM5', 38400)
        self.xbee = ZigBee(self.ser)
        print 'xbee created/initialized'
        return self

    def data_lines(self):
        while True:
            payload = ''
            for x in xrange(self.expected_packets):

                packet = self.xbee.wait_read_frame()
                while packet.get('id', None) == 'tx_status':
                    print('got tx_status frame')
                    packet = self.xbee.wait_read_frame()
                self.source_addr_long = packet.get(
                        'source_addr_long', self.source_addr_long)
                self.source_addr = packet.get(
                        'source_addr', self.source_addr)

                payload += packet['rf_data']
                if x < self.expected_packets - 1 and len(payload) < 100:
                    break;

            # let our data be processed
            yield self.data_shape.unpack(payload)

            # The key describing the device
            device_key = None
            for device_name, device_ip in DEVICES.items():
                print self.source_addr_long
                if device_ip == self.source_addr_long or device_ip == self.source_addr:
                    device_key = device_name
            if device_key is None:
                print("No command queue for device, assuming legacy mode and using the general queue.")
            outbound = self.outbound_queues[device_name]

            # flush the command queue to the xbee
            for cmd in outbound:
                self.xbee.tx(dest_addr_long=self.source_addr_long,
                        dest_addr=self.source_addr, data=cmd)
                print("command {}".format(' '.join("0x{:02x}".format(i) for i in cmd)))
                print("sent a command to {}".format(device_key))
                self.outbound_queues.get(device_key).clear()
            #self.xbee.tx(dest_addr_long=source_addr_long,
            #        dest_addr=source_addr, data=b'Hello world')


    def __exit__(self, type, value, traceback):
        self.xbee = None
        self.ser.close()
        if isinstance(value, serial.SerialException):
            print traceback
            return True
