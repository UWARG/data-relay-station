import serial
import struct
from xbee import XBee

db_type = (
        ('q', 'time'),
        ('d', 'lat'),
        ('d', 'lon'),
        ('f', 'pitch'),
        ('f', 'roll'),
        ('f', 'yaw'),
        ('f', 'pitch_rate'),
        ('f', 'roll_rate'),
        ('f', 'yaw_rate'),
        ('f', 'pitch_gain'),
        ('f', 'roll_gain'),
        ('f', 'yaw_gain'),
        ('f', 'pitch_setpoint'),
        ('f', 'roll_setpoint'),
        ('f', 'yaw_setpoint'),
        ('B', 'editing_gain'),
        ('x', ),            # Padding (comment out if no padding needed
        )

headers = ('time',
        'lat', 'lon',
        'pitch', 'roll', 'yaw',
        'pitch_rate', 'roll_rate', 'yaw_rate',
        'pitch_gain', 'roll_gain', 'yaw_gain',
        'pitch_setpoint', 'roll_setpoint', 'yaw_setpoint',
        'editing_gain' )

def main():

    try:
        ser = serial.Serial('/dev/ttyUSB0', 38400)
        xbee = XBee(ser)
        print 'xbee created/initialized'

        with open('flight_data.csv', 'w') as outfile:
            outfile.write(','.join(headers))
            outfile.write('\n')

        try:
            while True:
                packet = xbee.wait_read_frame()
                data = struct.unpack('qddfffffffffhhhhBx', packet['rf_data'])
                with open('flight_data.csv', 'a+w') as outfile:
                    outfile.write(','.join([str(i) for i in data]))
                    outfile.write('\n')

        except KeyboardInterrupt:
            print 'Process stopped by user'

        finally:
            xbee = None
            ser.close()

    except serial.SerialException:
        print 'failed to initialize serial connection'


if __name__ == '__main__':
    main()
