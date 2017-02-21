
#list of tcp connections
tcp_connections = {}

def add_connection(alias,port):
    tcp_connections[alias]=port

def remove_connection(alias):
    del tcp_connection[alias]

def get_connection(alias):
    return tcp_connection[alias]

def connections_to_string():
    str = ''
    items = tcp_connection.items()
    for i in items:
        str+= i[0]+':'+i[1]+','
    return str[:-1]
