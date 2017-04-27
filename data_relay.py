### data_relay.py

import datetime, time

from twisted.internet import reactor, threads
from receiver import Receiver, WriteToFileMiddleware
from comm_server import TelemetryFactory, ProducerToManyClient
from telem_producer import TelemetryProducer
from service_locator import ServiceProviderLocator

PACKET_TYPE_POSITION = 0
PACKET_TYPE_STATUS = 1
PACKET_TYPE_GAINS = 2
PACKET_TYPE_CHANNELS = 3

SERVICE_PORT = 1234

db_type = {
        PACKET_TYPE_POSITION: ( # 62 bytes + 0 padding bytes
            ('d', 'lat'),
            ('d', 'lon'),
            ('L', 'sys_time'),
            ('f', 'gps_time'),
            ('f', 'pitch'),
            ('f', 'roll'),
            ('f', 'yaw'),
            ('f', 'pitch_rate'),
            ('f', 'roll_rate'),
            ('f', 'yaw_rate'),
            ('f', 'airspeed'),
            ('f', 'altitude'),
            ('f', 'ground_speed'),
            ('h', 'heading')
            ),
        PACKET_TYPE_STATUS: ( # 49 bytes + 1 bytes padding
            ('f', 'path_checksum'), 
            ('h', 'roll_rate_setpoint'),
            ('h', 'pitch_rate_setpoint'),
            ('h', 'yaw_rate_setpoint'),
            ('h', 'roll_setpoint'),
            ('h', 'pitch_setpoint'),
            ('h', 'heading_setpoint'),
            ('h', 'altitude_setpoint'),
            ('h', 'throttle_setpoint'),
            ('h', 'internal_battery_voltage'),
            ('h', 'external_battery_voltage'),
            ('H', 'program_state'),
            ('H', 'autonomous_level'),
            ('H', 'startup_errors'),
            ('H', 'am_interchip_errors'),
            ('H', 'pm_interchip_errors'),
            ('H', 'gps_communication_errors'),
            ('H', 'dl_transmission_errors'),
            ('H', 'ul_receive_errors'),
            ('H', 'peripheral_status'),
            ('H', 'uhf_channel_status'),
            ('B', 'ul_rssi'),
            ('B', 'uhf_rssi'),
            ('B', 'uhf_link_quality'),
            ('B', 'waypoint_index'),
            ('B', 'waypoint_count'),
			('x', 'padding'),
            ),
        PACKET_TYPE_GAINS: ( # 92 bytes + 0 bytes of padding
            ('f', 'roll_rate_kp'),
            ('f', 'roll_rate_kd'),
            ('f', 'roll_rate_ki'),
            ('f', 'pitch_rate_kp'),
            ('f', 'pitch_rate_kd'),
            ('f', 'pitch_rate_ki'),
            ('f', 'yaw_rate_kp'),
            ('f', 'yaw_rate_kd'),
            ('f', 'yaw_rate_ki'),
            ('f', 'roll_angle_kp'),
            ('f', 'roll_angle_kd'),
            ('f', 'roll_angle_ki'),
            ('f', 'pitch_angle_kp'),
            ('f', 'pitch_angle_kd'),
            ('f', 'pitch_angle_ki'),
            ('f', 'heading_kp'),
            ('f', 'heading_ki'),
            ('f', 'altitude_kp'),
            ('f', 'altitude_ki'),
            ('f', 'ground_speed_kp'),
            ('f', 'ground_speed_ki'),
            ('f', 'path_kp'),
            ('f', 'orbit_kp')
            ),
        PACKET_TYPE_CHANNELS: ( #33 bytes + 1 byte of padding
            ('h', 'ch1_in'),
            ('h', 'ch2_in'),
            ('h', 'ch3_in'),
            ('h', 'ch4_in'),
            ('h', 'ch5_in'),
            ('h', 'ch6_in'),
            ('h', 'ch7_in'),
            ('h', 'ch8_in'),
            ('h', 'ch1_out'),
            ('h', 'ch2_out'),
            ('h', 'ch3_out'),
            ('h', 'ch4_out'),
            ('h', 'ch5_out'),
            ('h', 'ch6_out'),
            ('h', 'ch7_out'),
            ('h', 'ch8_out'),
            ('B', 'channels_scaled'),
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

def main(sim_file=None, sim_speed=0.2, serial_port=None, legacy_port=False, logging=True, uart=False):
    if logging:
        filename = "logs/flight_data_{}.csv".format(datetime.datetime.now()).replace(':','_').replace(' ','_');
        print ("writing to file called '{}'".format(filename))
    else:
        print ("Logging is disabled. Use --log to overwrite default.")

    list_header = [i[1] for key, value in db_type.iteritems() for i in value if not i[0] == 'x']
    #Add additional fields here:
    list_header.append('dl_rssi')
    header = ','.join(list_header)

    try:
        if sim_file:
            intermediate = DatalinkSimulator('logs/' + sim_file, sim_speed)
            with open('logs/' + sim_file) as simfile:
                header = simfile.readline()
        else:
            intermediate = Receiver(db_type, serial_port, uart)

        with intermediate as datalines:
            factory = TelemetryFactory(datalines, header)
            one2many = ProducerToManyClient()
            factory.setSource(one2many)

            if logging:
                telem = TelemetryProducer(one2many,
                        WriteToFileMiddleware(datalines, filename, header))
            else:
                telem = TelemetryProducer(one2many,datalines)

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
    parser.add_argument("--simfile", metavar="FILE", required=False, help="file to use for simulated data replay. File should be located in logs folder.")
    parser.add_argument("--simspeed", metavar="NUMBER", required=False, help="speed to play the simfile at in seconds per frame", default=0.2)
    parser.add_argument("--serialport", metavar="STRING", required=False, help="Preferred serial port if multiple devices are connected.")
    parser.add_argument("--uart", "-u", action='store_true', help="Connect to picpilot via uart instead of xbees.")
    parser.add_argument("--legacy_port", "-l", action='store_true', help="Disable automatic detection of IP and open a TCP connection on port 1234.")
    parser.add_argument("--log", action='store_true', help="Always write log file (even in simulator mode).")
    parser.add_argument("--nolog", action='store_true', help="Never write log file.")
    args = parser.parse_args()

    #Default Sim Speed
    simspeed = 0.2
    if (args.simspeed):
        simspeed = float(args.simspeed)

    #default log setting: log unless in simulator mode
    logging = not (args.simfile)
    if(args.log):
        logging=True
    elif(args.nolog):
        logging=False

    main(sim_file=args.simfile, sim_speed=simspeed, serial_port=args.serialport, legacy_port=args.legacy_port, logging=logging, uart=args.uart)
