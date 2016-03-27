### data_relay.py

import datetime, time
import argparse

from twisted.internet import reactor, threads
from receiver import Receiver, WriteToFileMiddleware
from comm_server import TelemetryFactory, ProducerToManyClient
from telem_producer import TelemetryProducer

db_type = [(
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
        ),
        (
        ('h', 'last_command_sent'),
        ('h', 'battery_level1'),
        ('h', 'battery_level2'),
        ('h', 'startup_error_codes'),
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
        ('h', 'roll_rate_setpoint'),
        ('h', 'roll_setpoint'),
        ('h', 'pitch_rate_setpoint'),
        ('h', 'pitch_setpoint'),
        ('h', 'throttle_setpoint'),
        ('h', 'yaw_rate_setpoint'),
        ('h', 'heading_setpoint'),
        ('h', 'altitude_setpoint'),
        ('h', 'flap_setpoint'),
        ('B', 'wireless_connection'),
        ('B', 'autopilot_active'),
        ('B', 'gps_status'),
        ('B', 'path_checksum'),
        ('B', 'waypoint_count'),
        ('B', 'waypoint_index'),
        ('B', 'path_following'),
        ('x', 'one byte of padding'),
        ),
        (
        ('f', 'roll_kd'),
        ('f', 'roll_kp'),
        ('f', 'roll_ki'),
        ('f', 'pitch_kd'),
        ('f', 'pitch_kp'),
        ('f', 'pitch_ki'),
        ('f', 'yaw_kd'),
        ('f', 'yaw_kp'),
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
        ('h', 'camera_status'),
        )
            ]

class DatalinkSimulator:

    def __init__(self, filename):
        print('initing {}'.format(self.__class__))
        self._filename = filename

    def data_lines(self):
        with open(self._filename, 'r') as infile:
            # skip the header line
            infile.next()
            for line in infile:
                #print 'yielding line'
                yield line
                time.sleep(0.2)

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

def main(sim_file=None):

    filename = "flight_data {}.csv".format(datetime.datetime.now()).replace(':','_')
    print "writing to file called '{}'".format(filename)

            
    header = ','.join([i[1] for i in db_type if not i[0] == 'x'])


    try:
        if sim_file:
            intermediate = DatalinkSimulator(sim_file)
            with open(sim_file) as simfile:
                header = simfile.readline()
        else:
            intermediate = Receiver(db_type)

        with intermediate as datalines:
            factory = TelemetryFactory(datalines, header)
            one2many = ProducerToManyClient()
            telem = TelemetryProducer(one2many,
                    WriteToFileMiddleware(datalines, filename, header))
            factory.setSource(one2many)

            print('listening on a port')
            reactor.listenTCP(1234, factory)
            print('running reactor')

            threads.deferToThread(telem.resumeProducing)
            reactor.run()
    except KeyboardInterrupt:
        print("Capture interrupted by user")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read data from xbee, write it locally and replay it over the network to connected clients.")
    parser.add_argument("--simfile", metavar="FILE", required=False, help="file to use for simulated data replay")
    args = parser.parse_args()
    main(sim_file=args.simfile)
