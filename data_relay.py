import datetime, time

from twisted.internet import reactor
from receiver import Receiver, WriteToFileMiddleware
from comm_server import TelemetryFactory, ProducerToManyClient
from telem_producer import TelemetryProducer

db_type = (
        ('q', 'time'),
        ('d', 'lat'),
        ('d', 'lon'),
        ('f', 'pitch'),
        ('f', 'roll'),
        ('f', 'yaw'),
        ('f', 'pitch_rate'),
        ('f', 'roll_rate'),
        ('f', 'yaw_rate'),
        ('f', 'pitch_gain'),
        ('f', 'roll_gain'),
        ('f', 'yaw_gain'),
        ('h', 'pitch_setpoint'),
        ('h', 'roll_setpoint'),
        ('h', 'yaw_setpoint'),
        ('h', 'throttle_setpoint'),
        ('B', 'editing_gain'),
        ('x', 'one byte of padding'),
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
                print 'yielding line'
                yield line
                time.sleep(0.01)

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
        with DatalinkSimulator('flight_data1.csv') as datalines:
            #print('datalines: {}'.format(datalines))
        #with Receiver(db_type) as datalines:
            factory = TelemetryFactory()
            one2many = ProducerToManyClient( factory )
            #middleware = WriteToFileMiddleware(datalines, filename, header)
            telem = TelemetryProducer(one2many, datalines)
            #reactor.callFromThread(telem.resumeProducing)
            #telem.resumeProducing()
            factory.setSource(one2many)
            print('listening on a port')
            reactor.listenTCP(1234, factory)
            print('running reactor')
            reactor.run()
    except KeyboardInterrupt:
        print("Capture interrupted by user")



if __name__ == "__main__":
    main()
