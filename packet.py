'''
Packet information. 
Class can automatically create packet following scoreboard modifications.

To modify the packet, modify the public variable 'scoreboard' from the class instance. 
'''

from scoreboard import scoreboard
from lfsr import whiten_bytes, print_bytes, byte_arr_to_bytes, aes_decrypt, aes_encrypt, crc_bytes, convert_hex_string_to_arr

'''
Packet format: 
- Preamble: 4-5 bytes of alternating 0s and 1s
- Sync Word: 0x2DD4 - 2 bytes 
- Length: 1 byte. 
- Payload: 32 or 64 bytes depending on the request type. 
- CRC: 2 bytes
- End-amble: 10 bytes, NOT required though.

Other notes: 
- Payload: AES 128 encrypted with EBC mode.
- Length, Payload (after encryption) and CRC are data whitened.
'''
class packet: 

    def __init__(self, initial_data = [], teams=False):

        self.preamble = [0xAA] * 5
        self.sync_word = [0x2D, 0xD4]

        # A default state
        if(initial_data == []):

            # scoreboard class is for the data in the payload
            self.scoreboard = scoreboard(teams=teams) # Payload section

        # Initialize data in the scoreboard
        else: 
            self.scoreboard = scoreboard(byte_array=initial_data, teams=len(initial_data) > 21)
        
        if(teams == True):
            # Large packet size
            self.length = [0x34]
        else: 
            # Small packet size
            self.length = [0x19]

        self.crc = [0x0, 0x0] # 2 byte CRC

    # Get the string
    def __str__(self): # Gets the data as a string.
        packet_data = self.get_byte_data()
        return str(packet_data)

    # Get the BYTE to send
    def get_byte_data(self):
        # Initial part of the packet
        packet_data = self.preamble + self.sync_word 

        # Encrypt the data
        encrypted_data = [x for x in self.encrypted_data()]
        
        # Calculate the CRC
        crc_data = self.length + encrypted_data
        crc_data = crc_bytes(bytearray(crc_data)) # CRC data
        hex_string = hex(crc_data)[2:].rjust(4,'0') # Padding trailing zeros. 
        crc_byte1 = int(hex_string[0:2], 16) # Byte1
        crc_byte2 = int(hex_string[2:4], 16) # Byte2
        self.crc = [crc_byte1, crc_byte2]

        # Whiten the bytes to send. Need to whiten length, payload and CRC
        unwhitened_data = self.length + encrypted_data + self.crc
        whitened_data = whiten_bytes(bytearray(unwhitened_data))

        # Add original data with the whitened bytes and a chain of 0xA's at the end.
        packet_data = packet_data + whitened_data + self.preamble
        return packet_data 
    
    def get_raw(self):
        my_data = self.get_byte_data()
        data_packet = []
        for byte in my_data:
            data = byte
            data = bin(byte)[2:].rjust(8,'0')
            
            tmp_values = []
            for bit in data: 
                tmp_values.append(int(bit))
            data_packet += tmp_values
        
        return data_packet

    '''
    Gets the data from the scoreboard, adds the filler bytes and encrypts all of it.
    '''
    def encrypted_data(self):

        # Convert string to bytes
        data = [0xff,0xff,0x0,0x0] + [ord(x) for x in str(self.scoreboard)] # Bytes in the packet
        data = byte_arr_to_bytes(data)
        return aes_encrypt(data)

    '''
    Get the unencrypted payload information
    '''
    def get_payload(self, is_string=False, padded_data=False):
        data = [ord(x) for x in str(self.scoreboard)]
        if(padded_data == True):
            data = [0xff,0xff,0x0,0x0] + data

        if(is_string == True):
            return str(data)
        return data

    # Set CRC and things. Necessary for other information to make sense. 
    def set_data(self):
        self.get_byte_data()

if __name__ == "__main__":
    # Packet information!
    #init_data = [0x34,0x30,0x32,0x35,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x31,0x30,0x33,0x33,0x48,0x4e,0x43,0x47, 0x30, 0x4A, 0x45, 0x53, 0x53, 0x45, 0x2D, 0x2D, 0x2D, 0x2D, 0x2D, 0x2D, 0x2D, 0x2D, 0x4D, 0x41, 0x58, 0x57, 0x45, 0x4C,0x4C]
    #init_data = [0x33,0x30,0x32,0x35,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x31,0x30,0x33,0x33,0x48,0x4e,0x43,0x52,0x31,0x49,0x4f,0x4d,0x45,0x2d,0x2d,0x2d,0x2d,0x2d,0x2d,0x2d,0x2d,0x2d,0x47,0x55,0x45,0x53,0x54,0x2d,0x2d,0x2d,0x2d,0x2d,0x2d,0x2d,0x2d]
    init_data = [0x32,0x35,0x32,0x33,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x31,0x30,0x33,0x33,0x47,0x4e,0x43,0x52,0x4e,0x48,0x4f,0x4d,0x45,0x2d,0x2d,0x2d,0x2d,0x2d,0x2d,0x2d,0x2d,0x2d,0x47,0x55,0x45,0x53,0x54,0x2d,0x2d,0x2d,0x2d,0x39,0x2d,0x2d,0x2d]
    my_packet = packet(teams=True, initial_data=init_data)

    my_data = str(my_packet.scoreboard)
    print_bytes(my_packet.get_byte_data())
    print(my_data)


