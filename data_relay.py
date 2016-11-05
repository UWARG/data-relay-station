### data_relay.py

import datetime, time

from twisted.internet import reactor, threads
from receiver import Receiver, WriteToFileMiddleware
from comm_server import TelemetryFactory, ProducerToManyClient
from telem_producer import TelemetryProducer
from service_locator import ServiceProviderLocator

HIGH_FREQ = 0
MED_FREQ = 1
LOW_FREQ = 2

SERVICE_PORT = 1234

db_type = {
        HIGH_FREQ: ( #76 bytes
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
        MED_FREQ: ( #82 bytes
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
        LOW_FREQ: ( #74 bytes + 12 padding bytes
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

def _get_service_host():
    import netifaces
    local_ip_addresses = []
    for interface in netifaces.interfaces():
        # Filter out loopback and virtual interfaces
        if interface == 'lo' or 'vir' in interface:
            continue
        iface = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
        if iface != None:
            for link in iface:
                local_ip_addresses.append(link['addr'])

    local_ip_address = None
    if len(local_ip_addresses) != 0:
        local_ip_address = local_ip_addresses[0]

    print("{}".format(local_ip_address))
    return local_ip_address

class DatalinkSimulator:

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

def main(sim_file=None, sim_speed=0.2, serial_port=None, legacy_port=False):

    filename = "flight_data {}.csv".format(datetime.datetime.now()).replace(':','_')
    print ("writing to file called '{}'".format(filename))
    
    list_header = [i[1] for key, value in db_type.iteritems() for i in value if not i[0] == 'x']
    #Add additional fields here:
    list_header.append('RSSI')
    header = ','.join(list_header)

    try:
        if sim_file:
            intermediate = DatalinkSimulator(sim_file, sim_speed)
            with open(sim_file) as simfile:
                header = simfile.readline()
        else:
            intermediate = Receiver(db_type, serial_port)

        with intermediate as datalines:
            factory = TelemetryFactory(datalines, header)
            one2many = ProducerToManyClient()
            telem = TelemetryProducer(one2many,
                    WriteToFileMiddleware(datalines, filename, header))
            factory.setSource(one2many)

            print('listening on a port')
            host = reactor.listenTCP(SERVICE_PORT if legacy_port else 0, factory).getHost()
            print('listening on port {}'.format(host.port))

            if legacy_port:
                print('auto discovery disabled in legacy port mode')
            else:
                reactor.listenUDP(SERVICE_PORT, ServiceProviderLocator(host.port))

            threads.deferToThread(telem.resumeProducing)
            reactor.run()
    except KeyboardInterrupt:
        print("Capture interrupted by user")



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Read data from xbee, write it locally and replay it over the network to connected clients.")
    parser.add_argument("--simfile", metavar="FILE", required=False, help="file to use for simulated data replay")
    parser.add_argument("--simspeed", metavar="NUMBER", required=False, help="speed to play the simfile at in seconds per frame", default=0.2)
    parser.add_argument("--serialport", metavar="STRING", required=False, help="Preferred serial port if multiple devices are connected.")
    parser.add_argument("--legacy_port", "-l", action='store_true')
    args = parser.parse_args()
    
    #Default Sim Speed
    simspeed = 0.2
    if (args.simspeed):
        simspeed = float(args.simspeed)
    main(sim_file=args.simfile, sim_speed=simspeed, serial_port=args.serialport, legacy_port=args.legacy_port)
