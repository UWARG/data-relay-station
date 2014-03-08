import datetime, time

from twisted.internet import reactor, threads
from receiver import Receiver, WriteToFileMiddleware
from comm_server import TelemetryFactory, ProducerToManyClient
from telem_producer import TelemetryProducer

db_type = (
        ('d', 'lat'),
        ('d', 'lon'),
        ('f', 'time'),
        ('f', 'pitch'),
        ('f', 'roll'),
        ('f', 'yaw'),
        ('f', 'pitch_rate'),
        ('f', 'roll_rate'),
        ('f', 'yaw_rate'),
        ('f', 'pitch_gain'),
        ('f', 'roll_gain'),
        ('f', 'yaw_gain'),
        ('f', 'heading'),
        ('f', 'ground_speed'),
        ('f', 'pitch_setpoint'),
        ('f', 'roll_setpoint'),
        ('f', 'heading_setpoint'),
        ('f', 'throttle_setpoint'),
        ('f', 'altitude_setpoint'),
        ('f', 'altitude'),
        ('h', 'int_pitch_setpoint'),
        ('h', 'int_roll_setpoint'),
        ('h', 'int_yaw_setpoint'),
        ('h', 'int_throttle_setpoint'),
        ('B', 'editing_gain'),
        ('B', 'gpsStatus'),
        #('x', 'one byte of padding'),
        )

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
                time.sleep(0.5)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        print('printing traceback')
        print(traceback)
        print('end of traceback')
        pass

def main():

    filename = "flight_data {}.csv".format(datetime.datetime.now())
    print "writing to file called '{}'".format(filename)

            
    header = ','.join([i[1] for i in db_type if not i[0] == 'x'])


    try:
        #with DatalinkSimulator('flight_data1.csv') as datalines:
        with Receiver(db_type) as datalines:
            factory = TelemetryFactory(datalines)
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
    main()
