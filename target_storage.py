import argparse

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor


class MultiEcho(Protocol):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        for history_line in self.factory.history:
            self.transport.write(history_line)
        self.factory.echoers.append(self)

    def dataReceived(self, data):
        self.factory.history.append(data)
        for echoer in self.factory.echoers:
            echoer.transport.write(data)

    def connectionLost(self, reason):
        self.factory.echoers.remove(self)


class MultiEchoFactory(Factory):

    def __init__(self):
        self.echoers = []
        self.history = []

    def buildProtocol(self, addr):
        return MultiEcho(self)


def main():
    reactor.listenTCP(4321, MultiEchoFactory())
    reactor.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A server to re-echo any data sent to it, as well as the history of all data for this session.")
    args = parser.parse_args()
    main()
