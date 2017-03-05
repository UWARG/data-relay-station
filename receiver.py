
### receiver.py

import serial
import Queue
import struct
from xbee.zigbee import ZigBee
from sys import platform as _platform
import time, datetime
import glob
import util, downlink_data
from txXBee.protocol import txXBee
from twisted.internet.serialport import SerialPort
from twisted.internet.task import LoopingCall


# The max allowed size for an api packet
MAX_PACKET_SIZE = 100

#logs path
LOG_PATH = 'logs/'
class Logger:
    """Take a generator, write each element out to file and
    forward it
    """
    def __init__(self, filename):
        print('initing {}'.format(self.__class__))
    #init file names and headers
        self.debug_filename = LOG_PATH + filename + '.txt'
        self.data_filename = LOG_PATH + filename + '.csv'
        self.header = downlink_data.get_headers()
    #create directory if one doesn't already exist
        util.create_directory(LOG_PATH)
    #open files
        self.debug_file = open(self.debug_filename, 'w')
        self.data_file = open(self.data_filename, 'w')
    #write headers to file
        self.data_file.write("{}\r\n".format(self.header))

    def debug(self,message):
        #write to debug file
        self.debug_file.write(message + '\n')
    def write_packet_to_file(self,packet_string):
        #write to csv file
        parsed_packet_string = str(packet_string).replace('(','').replace(')','').replace('None','') + '\n'
        self.data_file.write(parsed_packet_string)

    def __del__(self):
        self.debug_file.close()
        self.data_file.close()
class CommandQueue:
    def __init__(self, receiver, reactor):
        self.commands = Queue.Queue()
        self.receiver = receiver
        self.reactor = reactor
    def async_command(self, command):
        self.commands.put(command)
    def send_command(self):
        if not self.commands.empty():
            command = self.commands.get()
            self.reactor.callFromThread(self.receiver.send,
    			          "tx",
    			          dest_addr_long=command.get_addr_long(),
    			          dest_addr=command.get_addr(),
    			          data=command.get_data())
class Command:
    def __init__(self, cmd, vehicle):
        self.cmd = cmd
        self.vehicle = vehicle
    def get_data(self):
        return cmd
    def get_addr(self):
        return self.vehicle.get_addr()
    def get_addr_long(self):
        return self.vehicle.get_addr_long()

class Vehicle:
    def __init__(self, addr, addr_long, alias, reactor):
        self.addr = addr
        self.addr_long = addr_long
        self.reactor = reactor
        #create new TCPConnection
        self.create_tcp()
        #setup logging
        filename = "flight_{}_{}".format(datetime.datetime.now(),serialport).replace(':','_').replace(' ','_')
        self.logger = Logger(filename)

    def get_port(self):
        return self.connection.get_port()

    def write_packet(self,packet):
        self.logger.write_packet_to_file(packet)
        self.connection.write(packet)

    def create_tcp(self):
        self.producer = ProducerToManyClient()
        factory = TelemetryFactory()
        factory.setSource(self.producer)
        self.port = self.reactor.listenTCP(port, factory).getHost().port
        #add to network_manager
        network_manager.add_connection(alias, self.port)

class Receiver(txXBee):
    def __init__(self, serialport):
        print('init Receiver on ' + serialport )
        super(Receiver, self).__init__(escaped=True)
        self.data_shape = downlink_data.get_data_shape()

        #Check if all packets have the same size
        if not downlink_data.packets_are_same_size():
            downlink_data.print_packet_sizes()
            raise ValueError("Data packet size mismatch")

        self.expected_packets = downlink_data.get_data_size() / MAX_PACKET_SIZE + 1
        self.packet_type = None
        self.outbound = []
        self.rssi = -100
        self.stored_data = [tuple([None])]*len(self.data_shape.keys())
        self.vehicles = {}
        print('finished init Receiver on ' + serialport )

    def handle_packet(self, packet):
        payload = ''
        yield_data = ()

        print packet
        #check if packet is something other than incoming data
        if packet.get('id', None) != 'rx':
            #Checks for tx_response
            if packet.get('id', None) == 'tx_status':
                print('got tx_status frame')
            #Checks for command response and signal strength
            elif packet.get('id', None) == 'at_response':
                if packet.get('command', None) == 'DB':
                    self.rssi = ord(packet.get('parameter',self.rssi))
        else:

            source_addr_long = packet.get(
                    'source_addr_long')
            source_addr = packet.get(
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

            if source_addr_long not in self.vehicles:
                self.vehicles[source_addr_long] = Vehicle(source_addr, source_addr_long)
                print('added vehicle ' + source_addr_long)

            #write data to corresponding vehicle
            self.vehicles[source_addr_long].write_packet(yield_data)





        # flush the command queue to the xbee
        '''for cmd in self.outbound:
            self.xbee.tx(dest_addr_long=self.source_addr_long,
                    dest_addr=self.source_addr, data=cmd)
            print("command {}".format(' '.join("0x{:02x}".format(i) for i in cmd)))
            print("sent a command")'''
        self.outbound = []

    def async_tx(self, command):
        """Eventually send a command
        """
        self.outbound.append(command)

    def write_telem(self, packet):
        self.consumer.write(str(packet).replace("None", "") + "\r\n")

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
