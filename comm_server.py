import datetime
from twisted.protocols.pcp import BasicProducerConsumerProxy
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import interfaces, reactor

from receiver import Receiver, WriteToFileMiddleware

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



class ProducerToManyClientProxy(Protocol):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.clients.append(self)

    def dataReceived(self, data):
        for client in self.factory.clients:
            client.transport.write(data)

    def connectionLost(self, reason):
        self.factory.clients.remove(self):


class ProducerConsumerProxy(BasicProducerConsumerProxy):
    """Proxy which buffers a few telemetry blocks and drops old ones"""
    implements(interfaces.IPushProducer)

    def __init__(self, producer, consumer):
        self._paused = False
        self._buffer = deque(size = 10)
        self._producer = producer
        self._consumer = consumer
    
    def pauseProducing(self):
        self._paused = True

    def resumeProducing(self):
        self._paused = False
        for data in _buffer:
            self._consumer.write(data)

    def stopProducing(self):
        pass

    def write(self, data):
        self._buffer.append(data)

class ServeTelemetry(LineReceiver):
    """Serve the telemetry"""
    def connectionMade(self):
        # TODO: handshake stuff
        pass

    def lineReceiver(self, line):
        # TODO: continue handshake
        pass


    def connectionLost(self, reason):
        print('connection lost from {}'.format(self.transport.getPeer()))

def main():

    filename = "flight_data {}.csv".format(datetime.datetime.now())
    print "writing to file called '{}'".format(filename)

            
    header = ','.join([i[1] for i in db_type if not i[0] == 'x'])

    try:
        with Receiver(db_type) as datalines:
            for line in WriteToFileMiddleware(datalines, filename, header):
                pass
    except KeyboardInterrupt:
        print "Capture interrupted by user"



if __name__ == "__main__":
    main()
