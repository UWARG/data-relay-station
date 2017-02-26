### data_relay.py

import datetime, time, util, network_manager, downlink_data
from twisted.internet import threads, reactor
from receiver import Receiver, ReceiverSimulator
from comm_server import TelemetryFactory, ProducerToManyClient
from telem_producer import TelemetryProducer
from service_locator import ServiceProviderLocator



SERVICE_PORT = 1234

class XBee:
    def __init__(self,serialport):
        self.serialport = serialport
        #self.filename = "logs/flight_data_{}_{}.csv".format(datetime.datetime.now(),self.serialport).replace(':','_').replace(' ','_')
        self.header = downlink_data.get_headers()

        one2many = ProducerToManyClient()
        datalines = Receiver(self.serialport, one2many)
        factory = TelemetryFactory(datalines, self.header)
        factory.setSource(one2many)
        #self.host = reactor.listenTCP(0, factory).getHost()
        #self.port = self.host.port
        self.port = 1235
        print('listening on port {}'.format(self.port))

        network_manager.add_connection(self.serialport,self.port)

    def get_middleware(self, datalines):
        #return WriteToFileMiddleware(datalines, self.filename, self.header)
        return datalines

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
    def __init__(self, simfiles='',simspeed=0.2):
        self.simfiles = simfiles.split(',')
        self.simspeed = simspeed
        self.reset_all()

        print(network_manager.connections_to_string())
        #reactor.run()
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
