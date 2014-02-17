from twisted.internet import interfaces
from zope.interface import implements

class TelemetryProducer:
    """Produce the """
    implements(interfaces.IPushProducer)

    def __init__(self, consumer, gen):
        print('initing {}'.format(self.__class__))
        print(consumer)
        self._gen = gen
        self._consumer = consumer
        self._paused = False

    def resumeProducing(self):
        print('resuming producing of {}'.format(self.__class__))
        for i in self._gen.data_lines():
            #print('{}'.format(i))
            self._consumer.protocol.write(i)

    def stopProducing(self):
        pass
