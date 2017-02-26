import struct

HIGH_FREQ = 0
MED_FREQ = 1
LOW_FREQ = 2

db_type = {
        HIGH_FREQ: ( # 72 bytes + 16 padding bytes
            ('d', 'lat'),
            ('d', 'lon'),
            ('l', 'sys_time'),
            ('f', 'time'),
            ('f', 'pitch'),
            ('f', 'roll'),
            ('f', 'yaw'),
            ('f', 'pitch_rate'),
            ('f', 'roll_rate'),
            ('f', 'yaw_rate'),
            ('f', 'airspeed'),
            ('f', 'altitude'),
            ('f', 'ground_speed'),
            ('h', 'heading'),
            ('h', 'roll_rate_setpoint'),
            ('h', 'roll_setpoint'),
            ('h', 'pitch_rate_setpoint'),
            ('h', 'pitch_setpoint'),
            ('h', 'throttle_setpoint'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ),
        MED_FREQ: ( # 88 bytes
            ('f', 'roll_kd'),
            ('f', 'roll_kp'),
            ('f', 'pitch_kd'),
            ('f', 'pitch_kp'),
            ('f', 'yaw_kd'),
            ('f', 'yaw_kp'),
            ('f', 'path_checksum'),
            ('h', 'last_command_sent0'),
            ('h', 'last_command_sent1'),
            ('h', 'last_command_sent2'),
            ('h', 'last_command_sent3'),
            ('h', 'battery_level1'),
            ('h', 'battery_level2'),
            ('h', 'ch1in'),
            ('h', 'ch2in'),
            ('h', 'ch3in'),
            ('h', 'ch4in'),
            ('h', 'ch5in'),
            ('h', 'ch6in'),
            ('h', 'ch7in'),
            ('h', 'ch8in'),
            ('h', 'ch1out'),
            ('h', 'ch2out'),
            ('h', 'ch3out'),
            ('h', 'ch4out'),
            ('h', 'ch5out'),
            ('h', 'ch6out'),
            ('h', 'ch7out'),
            ('h', 'ch8out'),
            ('h', 'camera_status'),
            ('h', 'yaw_rate_setpoint'),
            ('h', 'heading_setpoint'),
            ('h', 'altitude_setpoint'),
            ('h', 'flap_setpoint'),
            ('B', 'wireless_connection'),
            ('B', 'autopilot_active'),
            ('B', 'gps_status'),
            ('B', 'waypoint_count'),
            ('B', 'waypoint_index'),
            ('B', 'path_following'),
            ),
        LOW_FREQ: ( # 75 bytes + 13 padding bytes
            ('f', 'roll_ki'),
            ('f', 'pitch_ki'),
            ('f', 'yaw_ki'),
            ('f', 'heading_kd'),
            ('f', 'heading_kp'),
            ('f', 'heading_ki'),
            ('f', 'altitude_kd'),
            ('f', 'altitude_kp'),
            ('f', 'altitude_ki'),
            ('f', 'throttle_kd'),
            ('f', 'throttle_kp'),
            ('f', 'throttle_ki'),
            ('f', 'flap_kd'),
            ('f', 'flap_kp'),
            ('f', 'flap_ki'),
            ('f', 'path_gain'),
            ('f', 'orbit_gain'),
            ('h', 'autonomousLevel'),
            ('h', 'startup_error_codes'),
            ('h', 'startupSettings'),
            ('B', 'probe_status'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            ('x', 'one byte of padding'),
            )
        }

def get_db_type():
    return db_type
def get_headers():
    #generate headers
    list_header = [i[1] for key, value in db_type.iteritems() for i in value if not i[0] == 'x']
    #Add additional fields here:
    list_header.append('RSSI')
    return ','.join(list_header)
def get_data_shape():
    return {key:struct.Struct(
        ''.join(map(lambda x: x[0], packet))) for key, packet in db_type.iteritems()}
def get_data_size():
    data_shape = get_data_shape()
    return data_shape[data_shape.keys()[0]].size
def packets_are_same_size():
    #Check if all packets have the same size
    data_shape = get_data_shape()
    data_size = get_data_size()
    for i in xrange(1,len(data_shape)):
        if (data_shape[i].size != data_size):
            return False
    return True
def print_packet_sizes():
    #Print out packet size
    for key, packet in self.data_shape.iteritems():
        print("Packet Size {}: {}".format(key,packet.size))
