import serial
import struct
from xbee.zigbee import ZigBee

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
                outfile.write(line)
            # re-yield element
            yield line


class Receiver:

    def __init__(self, db_type):
        self.data_shape = struct.Struct(
            ''.join(map(lambda x: x[0], db_type)))
        self.data_size = self.data_shape.size
        self.expected_packets = self.data_size / MAX_PACKET_SIZE + 1

    def __enter__(self):
        self.ser = serial.Serial('/dev/ttyUSB0', 38400)
        self.xbee = ZigBee(self.ser)
        print 'xbee created/initialized'
        return self

    def data_lines(self):
        while True:
            payload = ''
            for x in xrange(self.expected_packets):
                packet = self.xbee.wait_read_frame()
                payload += packet['rf_data']
                if x < self.expected_packets - 1 and len(payload) < 100:
                    break;
            yield self.data_shape.unpack(payload)


    def __exit__(self, type, value, traceback):
        self.xbee = None
        self.ser.close()
        if isinstance(value, serial.SerialException):
            print traceback
            return True
