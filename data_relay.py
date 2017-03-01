
tro==### data_relay.py

import datetime, time, util, network_manager, downlink_data
from network_manager import TCPConnection
from twisted.internet import threads, reactor
from receiver import Receiver, ReceiverSimulator
from comm_server import TelemetryFactory, ProducerToManyClient
from telem_producer import TelemetryProducer
from service_locator import ServiceProviderLocator
from twisted.internet.serialport import SerialPort



SERVICE_PORT = 1234



class XBee(SerialPort):
    def __init__(self,serialport, reactor):
        super.__init__(XBee,Receiver(self.serialport), serialport, reactor, 115200)
        print('listening on port {}'.format(self.connection.get_port()))
    def connectionLost(self, reason):
        super.connectionLost(Xbee,reason)
        print('Xbee connection ' + self.serialport + ' lost.')
        
class XBeeSimulator(XBee):
    def __init__(self,simfile,speed):
        self.simfile = simfile
        self.speed = speed
        self.header = self.get_headers()

        self.header = self.get_headers()
        datalines = ReceiverSimulator('logs/' + simfile, speed)
        self.port = self.init_telemetry(datalines)

        network_manager.add_connection(self.simfile,self.port)

    def get_headers(self):
        with open('logs/' + self.simfile) as simfile:
            return simfile.readline()

    def get_middleware(self,datalines):
        return datalines

class DataRelay:
    def __init__(self):
        self.reset_xbees()

        print(network_manager.connections_to_string())
        reactor.run()
    def refresh_xbees(self):
        #find xbee serial ports
        ports = util.detect_xbee_ports()
        #make a connection for each one
        for port in ports:
            if port not in self._xbees:
                self._xbees[port] = (XBee(port,reactor))

    def reset_all(self):
        self._xbees = {}
        self.refresh_xbees()

class DataRelaySim(DataRelay):
    def __init__(self, simfiles='',simspeed=0.2):
        self.simfiles = simfiles.split(',')
        self.simspeed = simspeed
        self.reset_all()

        print(network_manager.connections_to_string())
        reactor.run()
    def refresh_xbees(self):
        ports = util.detect_xbee_ports()
        #make a connection for each one
        for port in ports:
            if port not in self._xbees:
                self._xbees[port] = (XBee(port))
    def refresh_sims(self):
        for simfile in self.simfiles:
            if simfile not in self._xbees and simfile!='':
                self._xbees[simfile] = (XBeeSimulator(simfile,self.simspeed))

    def reset_all(self):
        self._xbees = {}
        self.refresh_xbees()
        self.refresh_sims()
