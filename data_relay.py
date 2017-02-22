### data_relay.py

import datetime, time, util, network_manager
from twisted.internet import threads, reactor
from receiver import Receiver, ReceiverSimulator, WriteToFileMiddleware
from comm_server import TelemetryFactory, ProducerToManyClient
from telem_producer import TelemetryProducer
from service_locator import ServiceProviderLocator

HIGH_FREQ = 0
MED_FREQ = 1
LOW_FREQ = 2

SERVICE_PORT = 1234

db_type = {
        HIGH_FREQ: ( # 72 bytes + 16 padding bytes
            ('d', 'lat'),
            ('d', 'lon'),
            ('l', 'sys_time'),
            ('f', 'time'),
            ('f', 'pitch'),
            ('f', 'roll'),
            ('f', 'yaw'),
            ('f', 'pitch_rate'),
            ('f', 'roll_rate'),
            ('f', 'yaw_rate'),
            ('f', 'airspeed'),
            ('f', 'altitude'),
            ('f', 'ground_speed'),
            ('h', 'heading'),
            ('h', 'roll_rate_setpoint'),
            ('h', 'roll_setpoint'),
            ('h', 'pitch_rate_setpoint'),
            ('h', 'pitch_setpoint'),
            ('h', 'throttle_setpoint'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ),
        MED_FREQ: ( # 88 bytes
            ('f', 'roll_kd'),
            ('f', 'roll_kp'),
            ('f', 'pitch_kd'),
            ('f', 'pitch_kp'),
            ('f', 'yaw_kd'),
            ('f', 'yaw_kp'),
            ('f', 'path_checksum'),
            ('h', 'last_command_sent0'),
            ('h', 'last_command_sent1'),
            ('h', 'last_command_sent2'),
            ('h', 'last_command_sent3'),
            ('h', 'battery_level1'),
            ('h', 'battery_level2'),
            ('h', 'ch1in'),
            ('h', 'ch2in'),
            ('h', 'ch3in'),
            ('h', 'ch4in'),
            ('h', 'ch5in'),
            ('h', 'ch6in'),
            ('h', 'ch7in'),
            ('h', 'ch8in'),
            ('h', 'ch1out'),
            ('h', 'ch2out'),
            ('h', 'ch3out'),
            ('h', 'ch4out'),
            ('h', 'ch5out'),
            ('h', 'ch6out'),
            ('h', 'ch7out'),
            ('h', 'ch8out'),
            ('h', 'camera_status'),
            ('h', 'yaw_rate_setpoint'),
            ('h', 'heading_setpoint'),
            ('h', 'altitude_setpoint'),
            ('h', 'flap_setpoint'),
            ('B', 'wireless_connection'),
            ('B', 'autopilot_active'),
            ('B', 'gps_status'),
            ('B', 'waypoint_count'),
            ('B', 'waypoint_index'),
            ('B', 'path_following'),
            ),
        LOW_FREQ: ( # 75 bytes + 13 padding bytes
            ('f', 'roll_ki'),
            ('f', 'pitch_ki'),
            ('f', 'yaw_ki'),
            ('f', 'heading_kd'),
            ('f', 'heading_kp'),
            ('f', 'heading_ki'),
            ('f', 'altitude_kd'),
            ('f', 'altitude_kp'),
            ('f', 'altitude_ki'),
            ('f', 'throttle_kd'),
            ('f', 'throttle_kp'),
            ('f', 'throttle_ki'),
            ('f', 'flap_kd'),
            ('f', 'flap_kp'),
            ('f', 'flap_ki'),
            ('f', 'path_gain'),
            ('f', 'orbit_gain'),
            ('h', 'autonomousLevel'),
            ('h', 'startup_error_codes'),
            ('h', 'startupSettings'),
            ('B', 'probe_status'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            )
        }
class Vehicle:
    def __init__(self,serialport):
        self.serialport = serialport
        self.filename = "logs/flight_data_{}_{}.csv".format(datetime.datetime.now(),self.serialport).replace(':','_').replace(' ','_')
        self.header = self.get_headers()
        with Receiver(db_type, self.serialport) as datalines:
            self.port = self.init_telemetry(datalines)
        network_manager.add_connection(self.serialport,self.port)
        reactor.run()

    def get_headers(self):
        #generate headers
        list_header = [i[1] for key, value in db_type.iteritems() for i in value if not i[0] == 'x']
        #Add additional fields here:
        list_header.append('RSSI')
        return ','.join(list_header)

    def init_telemetry(self, datalines):
        self.factory = TelemetryFactory(datalines, self.header)
        one2many = ProducerToManyClient()
        self.factory.setSource(one2many)

        telem = TelemetryProducer(one2many,self.get_middleware(datalines))

        host = reactor.listenTCP(0, self.factory).getHost()
        print('listening on port {}'.format(host.port))

        threads.deferToThread(telem.resumeProducing)
        return host.port
    def get_middleware(self, datalines):
        return WriteToFileMiddleware(datalines, self.filename, self.header)

class VehicleSimulator(Vehicle):
    def __init__(self,simfile,speed):
        self.simfile = simfile
        self.speed = speed
        self.header = self.get_headers()

        self.header = self.get_headers()
        with ReceiverSimulator('logs/' + simfile, speed) as datalines:
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

    def refresh_vehicles(self):
        ports = util.detect_xbee_ports()
        #make a connection for each one
        for port in ports:
            if port not in self._vehicles:
                self._vehicles[port] = (Vehicle(port))
    def refresh_sims(self):
        for simfile in self.simfiles:
            if simfile not in self._vehicles and simfile!='':
                self._vehicles[simfile] = (VehicleSimulator(simfile,self.simspeed))

    def reset_all(self):
        self._vehicles = {}
        self.refresh_vehicles()
        self.refresh_sims()
