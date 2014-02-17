from collections import deque
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import interfaces
from zope.interface import implements



class ProducerToManyClient(Protocol):

    def __init__(self, factory):
        print('initing {}'.format(self.__class__))
        self.factory = factory

    def connectionMade(self):
        self.factory.clients.append(self)

    def dataReceived(self, data):
        for client in self.factory.clients:
            client.transport.write(data)

    def connectionLost(self, reason):
        self.factory.clients.remove(self)


class ProducerConsumerBufferProxy:
    """Proxy which buffers a few telemetry blocks and drops old ones"""
    implements(interfaces.IPushProducer, interfaces.IConsumer)

    def __init__(self, producer, consumer):
        print('initing {}'.format(self.__class__))
        self._paused = False
        self._buffer = deque(maxlen = 10)
        self._producer = producer
        self._consumer = consumer
    
    def pauseProducing(self):
        self._paused = True

    def resumeProducing(self):
        self._paused = False
        for data in self._buffer:
            self._consumer.write(data)

    def stopProducing(self):
        pass

    def write(self, data):
        self._buffer.append(data)

class ServeTelemetry(LineReceiver):
    """Serve the telemetry"""
    def __init__(self, producer):
        print('initing {}'.format(self.__class__))
        self._producer = producer
        self._firstConnect = True

    def connectionMade(self):
        if self._firstConnect:
            # TODO: setup controlling client
            self._firstConnect = False
        # TODO: handshake stuff
        proxy = ProducerConsumerBufferProxy(self, self._producer)
        self.transport.registerProducer(proxy, True)
        proxy.resumeProducing()
        pass

    def lineReceived(self, line):
        # TODO: continue handshake
        print('from {} received line {}'.format(
            self.transport.getPeer(), line))
        pass


    def connectionLost(self, reason):
        print('connection lost from {}'.format(self.transport.getPeer()))

class TelemetryFactory(Factory):

    def __init__(self):
        self.clients = []

    def setSource(self, telemetrySource):
        self._telemetrySource = telemetrySource

    def buildProtocol(self, addr):
        return ServeTelemetry(self._telemetrySource)

#class LoggingConsumer(
