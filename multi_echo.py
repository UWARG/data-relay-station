### multi_echo.py

from collections import deque
import argparse, datetime, time

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

import os,errno

DEFAULT_MAX_HISTORY_SIZE = 200

class EchoLogger:
    def __init__(self, file):
        self.file = file

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class MultiEcho(LineReceiver):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        for history_line in self.factory.history:
            self.transport.write(history_line)
        self.factory.echoers.append(self)
        self.logger = EchoLogger(open(self.factory.filename, "a"))

    def lineReceived(self, data):
        self.factory.history.append(data)
        self.logger.log(data)
        for echoer in self.factory.echoers:
            echoer.transport.write(data+"\r\n")

    def connectionLost(self, reason):
        self.factory.echoers.remove(self)
        self.logger.close()


class MultiEchoFactory(Factory):

    def __init__(self, history_size = DEFAULT_MAX_HISTORY_SIZE, logfile_name = None):
        self.echoers = []
        self.history = deque(maxlen = history_size)
        if logfile_name is None:
            self.filename = "logs/echo_data_{}.log".format(datetime.datetime.now()).replace(':', '_')
        print("writing to a file called '{}'".format(self.filename))

    def buildProtocol(self, addr):
        return MultiEcho(self)



def main(history_size):
    reactor.listenTCP(4321, MultiEchoFactory(history_size))
    reactor.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
            """A server to re-echo any data sent to it, as well as the history of all data for this session.""")
    parser.add_argument("--max_history", metavar="N", required=False, help="maximum history size for this server to store (default: 200)", default=DEFAULT_MAX_HISTORY_SIZE)
    args = parser.parse_args()
    main(args.max_history)
