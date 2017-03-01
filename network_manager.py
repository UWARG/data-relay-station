from comm_server import ProducerToManyClient
#list of tcp connections
tcp_connections = {}

def add_connection(alias,connection):
    tcp_connections[alias]=connection

def remove_connection(alias):
    del tcp_connections[alias]

def get_connection(alias):
    return tcp_connections[alias]

def connections_to_string():
    connection_string = ''
    items = tcp_connections.items()
    for item in items:
        connection_string+= str(item[0])+':'+str(item[1].get_port())+','
    return connection_string[:-1]


class TCPConnection:
    def __init__(self, reactor, port=0):
        self.producer = ProducerToManyClient()
        self.reactor = reactor
        factory = TelemetryFactory()
        factory.setSource(self.producer)
        self.host = reactor.listenTCP(port, factory).getHost()
    def get_port(self):
        return self.host.port
    def write(self, message):
        self.consumer.write(message)
