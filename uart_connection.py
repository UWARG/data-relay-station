DELIMITER= 0x7e
XBEE_FRAME_TYPE_TX_REQUEST  = 0x10
XBEE_FRAME_TYPE_RX_INDICATOR = 0x90
XBEE_FRAME_TYPE_AT_COMMAND = 0x08
class UARTConnection:

    def __init__(self,serial):
        self.serial = serial

    #wait until the next packet, and then parse the packet
    def wait_read_frame(self):
        #create empty packet
        packet = {}

        #wait until packet arrives
        byte = self.serial.read();
        while(len(byte)==1 and ord(byte)!=DELIMITER):
            byte = self.serial.read()

        #parse length bytes
        length =  ord(self.serial.read()) << 8
        length += ord(self.serial.read())

        #get packet data
        packet_data = self.serial.read(length)
        if(len(packet_data)<length):
            print('full packet not recieved')
            return {}
        #frame id is the first byte
        #check for incoming data
        if(ord(packet_data[0])==XBEE_FRAME_TYPE_TX_REQUEST):
            packet['id']='rx'

            #ignore 12 bytes of header data
            #store the rest in the packet
            packet['rf_data'] = packet_data[14:]

            #calculate what the checksum should be
            checksum = 0
            for byte in packet_data:
                checksum +=ord(byte)

            #get checksum and compare
            byte = ord(self.serial.read())
            if((checksum + byte) & 0xFF == 0xFF):
                return packet
            else:
                print('uart checksum incorrect!')

        #check for AT command
        elif(ord(packet_data[0])==XBEE_FRAME_TYPE_AT_COMMAND):
            packet['id'] = 'at_response'

            #get 2 command bytes
            packet['command'] = packet_data[2:4]
            return packet

        print('error in parsing uart with frame id ' + str(ord(packet_data[0])))
        return {}

    #used for rssi, which is pointless when you aren't actually using xbees
    def at(self,command=""):
        pass

    def tx(self, **kwargs):
        data = kwargs['data']
        #add 12 for the header information
        length = len(data)+12
        packet = ''
        packet+=chr(DELIMITER)
        packet+=chr(length >> 8)
        packet+=chr(length &  0xFF)

        #add frame_id
        packet+=chr(XBEE_FRAME_TYPE_RX_INDICATOR)
        #insert 11 padding bytes of header data
        for i in range(0,11):
            packet+=chr(0x0)

        packet+=data

        #checksum
        summ=XBEE_FRAME_TYPE_RX_INDICATOR
        for byte in data:
            summ+=byte
        checksum = 0xFF - (summ & 0xFF)
        packet+=chr(checksum)
        self.serial.write(packet)
