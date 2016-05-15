from twisted.internet.protocol import DatagramProtocol

class ServiceProviderLocator(DatagramProtocol):

    def __init__(self, host_port):
        self.host_port = host_port

    def datagramReceived(self, datagram, addr):
        try:
            origin_data = datagram.split(":")

            if len(origin_data) != 2:
                print("Invalid datagram from {}:{} that says {{{}}}. Should be of form <host>:<port>".format(addr[0], addr[1], datagram))
                return

            origin_host, origin_port = origin_data

            print("Got datagram from {}:{} for {}:{}".format(addr[0], addr[1], origin_host, origin_port))

            self.transport.write("{}".format(self.host_port), (origin_host, int(origin_port)))
        except Exception as e:
            print("Error in datagram processing: {}".format(e))
            print("Invalid datagram from {}:{} that says {{{}}}".format(addr[0], addr[1], datagram))
