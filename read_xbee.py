import serial
import struct
from xbee import XBee

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
                data = struct.unpack('qddfffffffffhhhcx', packet['rf_data'])
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
