import serial
import struct
from xbee import XBee

# The max allowed size for an api packet
MAX_PACKET_SIZE = 100


class WriteToFileMiddleware(object):
    """Take a generator, write each element out to file and
    forward it
    """
    def __init__(self, gen, filename, header):
        self.gen = gen
        self.filename = filename
        self.header = header

    def data_lines(self):
        # write data line out to file
        with open(self.filename, 'a+w') as outfile:
            outfile.write("{1}\n".format(header))

        for line in self.gen:
            # write element to file
            with open(self.filename, 'a+w') as outfile:
                data = data_shape.unpack(line)
                outfile.write(','.join([str(i) for i in data]))
                outfile.write('\n')
            # re-yield element
            yield i

class Receiver(object):

    def __init__(self, db_type):
        self.data_shape = struct.Struct(
            ''.join(map(lambda x: x[0], db_type)))
        self.data_size = self.data_shape.size
        self.expected_packets = self.data_size / MAX_PACKET_SIZE + 1

    def __enter__(self):
        self.ser = serial.Serial('/dev/ttyUSB0', 38400)
        self.xbee = XBee(ser)
        print 'xbee created/initialized'

    def data_lines(self):
        while True:
            payload = ''
            for x in xrange(self.expected_packets):
                packet = xbee.wait_read_frame()
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
