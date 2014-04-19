import serial
import struct
from xbee import XBee
rom sys import platform as _platform

# The max allowed size for an api packet
MAX_PACKET_SIZE = 100

db_type = (
        ('d', 'lat'),
        ('d', 'lon'),
        ('f', 'time'),
        ('f', 'pitch'),
        ('f', 'roll'),
        ('f', 'yaw'),
        ('f', 'pitch_rate'),
        ('f', 'roll_rate'),
        ('f', 'yaw_rate'),
        ('f', 'kd_gain'),
        ('f', 'kp_gain'),
        ('f', 'ki_gain'),
        ('f', 'ground_speed'),
        ('f', 'altitude'),
        ('h', 'heading'),
        ('h', 'pitch_setpoint'),
        ('h', 'roll_setpoint'),
        ('h', 'heading_setpoint'),
        ('h', 'throttle_setpoint'),
        ('h', 'altitude_setpoint'),
        ('h', 'int_pitch_setpoint'),
        ('h', 'int_roll_setpoint'),
        ('h', 'int_yaw_setpoint'),
        ('h', 'lastCommandSent'),
        ('h', 'errorCodes'),
        ('B', 'waypointIndex'),
        ('B', 'editing_gain'),
        ('B', 'gpsStatus'),
        ('x', 'one byte of padding'),
        )

def main():

    data_shape = struct.Struct(''.join(map(lambda x: x[0], db_type)))
    data_size = data_shape.size
    expected_packets = data_size / MAX_PACKET_SIZE + 1

    try:
        if _platform == "linux" or _platform == "linux2":
            ser = serial.Serial('/dev/ttyUSB0', 38400)
        elif _platform == "win32":
            self.ser = serial.Serial('COM5', 38400
        xbee = XBee(ser)
        print 'xbee created/initialized'

        with open('flight_data.csv', 'w') as outfile:
            outfile.write(','.join([i[1] for i in db_type if not i[0] == 'x']))
            outfile.write('\n')

        try:
            while True:
                payload = ''
                for x in xrange(expected_packets):
                    packet = xbee.wait_read_frame()
                    payload += packet['rf_data']
                    if x < expected_packets - 1 and len(payload) < 100:
                        break;

                # write data to file
                with open('flight_data.csv', 'a+w') as outfile:
                    data = data_shape.unpack(payload)
                    outfile.write(','.join([str(i) for i in data]))
                    outfile.write('\n')

        except KeyboardInterrupt:
            print 'Process stopped by user'

        finally:
            xbee = None
            ser.close()

    except serial.SerialException:
        print 'failed to initialize serial connection'



    main()
