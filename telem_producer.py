### telemetry_producer.py

from twisted.internet import interfaces
from zope.interface import implements

class TelemetryProducer:
    """Produce the """
    implements(interfaces.IPushProducer)

    def __init__(self, consumer, gen):
        print('initing {}'.format(self.__class__))
        print(consumer)
        self._consumer = consumer
        self._gen = gen
        self._paused = False

    def resumeProducing(self):
        print('resuming producing of {}'.format(self.__class__))
        for i in self._gen.data_lines():
            self._consumer.write(str(i)+"\r\n")

    def connectionMade(self):
        self.factory.clients.append(self)

    def dataReceived(self, data):
        for client in self.factory.clients:
            client.transport.write(data)

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
