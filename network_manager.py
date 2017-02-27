
#list of tcp connections
tcp_connections = {}

def add_connection(alias,port):
    tcp_connections[alias]=port

def remove_connection(alias):
    del tcp_connections[alias]

def get_connection(alias):
    return tcp_connections[alias]

def connections_to_string():
    connection_string = ''
    items = tcp_connections.items()
    for item in items:
        connection_string+= str(item[0])+':'+str(item[1])+','
    return connection_string[:-1]


class TCPConnection:
    def __init__(self, reactor, port=0):
        self.reactor = reactor
        one2many = ProducerToManyClient()
        factory = TelemetryFactory(self.header)
        factory.setSource(one2many)
        self.host = reactor.listenTCP(port, factory).getHost()
    def get_port()
        return self.host.port
    
