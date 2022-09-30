from Crypto.Cipher import AES
import crcmod 

'''
size: The length of the polynomial
taps: The values of the polynomial
initialization: The initial state of the LSFR.
iterations: The amount of bits to return from the LSFR
'''
def lfsr(size, taps, initialization=1, iterations=8):
    '''
    Treating this as the MOST significant bit being at the front and LEAST significant bit at the back.
    '''
    registers = [1] * size
    
    # Initialize the values with a custom number. Defaults to all 1s.
    if initialization != 1:
        for index in range(size):
            registers[index] = (initialization >> (size - index - 1)) & 1
        #print(registers)

    # Invert the taps to match the expected format
    taps = invert_taps(taps, size)

    # Checking for duplicates. 
    dict_check = {}

    # The bits to be outputted. 
    output_bits = []

    # Grab iterations amount of bits
    for i in range(iterations):

        # Copying the register since it is normally copy by reference instead of value.
        OG_reg = registers[:]
        #print(i, registers)
        input_bit = get_input_bit(taps, registers)

        # Remove the bit from the end of the list
        output_bit = registers.pop(-1)

        # The original state is invalid. So, we skip this.
        #if(i != 0): # <--- Ask Max Arnold about this!
        output_bits.append(output_bit)

        # Get the NEW bit to be inserted into the system and add it to the front of the list (MSB).
        registers.insert(0, input_bit)

        # Checking to see if we have seen this register state so far (dups)
        key = "".join([str(x) for x in OG_reg])
        if(key in dict_check):
            # Duplicates, the wrap around, cause issues. I don't know why!
            #print("Dup: ", key, OG_reg, dict_check[key], i)
            return output_bits
        dict_check[key] = i
    return output_bits

'''
The LFSR has an initial state. This is because it CANNOT start with 0x0 since it
will ALWAYS output a zero. 

From data sniffing, we know that there are two sizes with their corresponding whitened bytes:
- 0x19 - 0xe6
- 0x34 - 0xcb

The packet has the data whitened for the LENGTH, PAYLOAD and CRC. The PAYLOAD is encrypted though....
From the LENGTH, we need to find the initial state. There are ONLY two size values we have though.

The script below finds all seeds that match the outputs of the 0x19 size and 0x34 size. 
With this we KNOW the initial state of the LSFR! Outputs 0x1, 0xff and 0x1FF
'''
def brute_force_seed():

    print("Find matches for seeds!")
    # Go from 1-512 to brute force the initial state to be used. 
    for i in range(1, 512):
        # Most significant bit first
        output_bits = lfsr(9,[0, 5], initialization=i) 

        # Information of the smaller packet
        bits_arr1 = num_to_bits_arr(0xe6)
        whitened_byte1 = whiten_byte(bits_arr1, output_bits)
        whitened_byte1 = bits_arr_to_num(whitened_byte1)

        # Information on the larger packet
        bits_arr2 = num_to_bits_arr(0xcb)
        whitened_byte2 = whiten_byte(bits_arr2, output_bits)
        whitened_byte2 = bits_arr_to_num(whitened_byte2)

        # Whitened sized of the packets. Smaller and the larger packets.
        if(whitened_byte1 == 0x19 and whitened_byte2 == 0x34):
            print(hex(i))

def brute_force_seed2():

    print("Find matches for seeds!")
    # Go from 1-512 to brute force the initial state to be used. 
    for i in range(1, 512):
        # Most significant bit first
        output_bits = lfsr(9,[0, 5], initialization=i) 

        # Information of packet one for the FINAL byte
        bits_arr1 = num_to_bits_arr(0x47)
        whitened_byte1 = whiten_byte(bits_arr1, output_bits)
        whitened_byte1 = bits_arr_to_num(whitened_byte1)

        # Information on packet two for the FINAL byte
        bits_arr2 = num_to_bits_arr(0xC1)
        whitened_byte2 = whiten_byte(bits_arr2, output_bits)
        whitened_byte2 = bits_arr_to_num(whitened_byte2)

        # Whitened sized of the packets. Smaller and the larger packets.
        if(whitened_byte1 == 0x46 and whitened_byte2 == 0xC0):
            print(hex(i))

# Show the seed :) 
def show_seed():
    
    print("------------------")
    output_bits = lfsr(10,[0, 5, 9], initialization=510, iterations=8) # Flip because the list is 
    bits_arr = num_to_bits_arr(0x19) 
    whitened_byte = whiten_byte(bits_arr, output_bits)
    whitened_byte = bits_arr_to_num(whitened_byte)
    print(hex(whitened_byte))


    output_bits = lfsr(10,[0, 5, 9], initialization=510, iterations=8) # Flip because the list is 
    #print("LFSR Output: ", output_bits)
    bits_arr = num_to_bits_arr(0x34)
    whitened_byte = whiten_byte(bits_arr, output_bits)
    whitened_byte = bits_arr_to_num(whitened_byte)
    print(hex(whitened_byte))

'''
taps: The bits to use as the new input
register: The value of the current registers

'''
def get_input_bit(taps, registers):
    output_bit = 0
    for tap in taps:
        output_bit = output_bit ^ registers[tap]

    return output_bit

'''
Invert the taps to go with the needed representation.
Used at the beginning of the function.
'''
def invert_taps(taps, amount):
    new_taps = []
    for element in taps: 
        new_taps.append((amount-1)-element)
    
    return new_taps

'''
Whiten a series of bits with the LSFR bits. 

input: The characters that we need to whiten 
lsfr_bits: The characters outputted from the lsfr.

output: The whitened bytes. 
'''
def whiten_byte(input, lfsr_bits):
    output_arr = []

    if(len(input) > len(lfsr_bits)):
        print("LFSR bytes less than input")
        return False 

    for index in range(len(input)):
        bit = int(input[index])
        lfsr_bit = int(lfsr_bits[index])

        output_bit = bit ^ lfsr_bit

        output_arr.append(str(output_bit))
    return output_arr

'''
Convert a number into the binary representation in a list
'''
def num_to_bits_arr(num):
    data = list(bin(num)[2:].rjust(8,'0'))
    return data

'''
Converts a list of strings or numbers back into a number
'''
def bits_arr_to_num(arr):
    if(arr != [] and type(arr[0]) == int ):
        data = "".join([str(x) for x in arr])
        return int(data, 2) 
    elif(arr != []): 
        data = "".join(arr)
        return int(data, 2) 

'''
Given a collection of bytes, whiten/dewhiten ALL of them. 
It should be noted that since the XOR operation is used, whitening and dewhitening is the SAME process. 

bytes: A list of numbers, representing the bytes, to whiten. 

output: A list of the fully whitened bytes.
'''
def whiten_bytes(input_bytes):

    '''
    Generate the LFSR bits to use
    - 9,[0, 5] represents the polynomial x^9 + x^5 + 1. 
    - Initialization of 1 represents the STARTING point of the LFSR on the RF. 1 is the default (do nothing) and we initial everything to ALL 1s.
      module. This was brute forced by comparing the two bytes we KNOW (size) to confirm it. 
    - Iterations: Proportional to the AMOUNT of bytes being used. For every bit we need 
      to whiten/dewhiten we need to have a corresponding LSFR output bit as well.
    '''
    lfsr_bits = lfsr(9,[0, 5], initialization=1, iterations=len(input_bytes)*8)

    # Wrap around case for large packet. NO IDEA why this works :)
    if(len(lfsr_bits) == 512):
        # 0xFF, 0x1, 0xC3 for final byte of encryption and 2 bytes of CRC
        lfsr_bits += [1,1,1,1,1,1,1,1,  0,0,0,0,0,0,0,1,  1,1,0,0,0,0,1,1]

    output = []
    for byt in input_bytes:
        bits_arr = num_to_bits_arr(byt) 

        # Whiten the byte and append to output
        whitened_byte = whiten_byte(bits_arr, lfsr_bits)
        whitened_byte = bits_arr_to_num(whitened_byte)
        output.append(whitened_byte)

        # Remove the 8 previous bits used for the whitening 
        lfsr_bits = lfsr_bits[8:]

    return output

# Print out the bytes in a HEX format.
def print_bytes(byte_arr):
    for byt in byte_arr:
        byt = int(byt)
        print(hex(byt), end=',')
    print()

def byte_arr_to_bytes(byte_arr):
    output = b""
    for byt in byte_arr:
        byt = byt.to_bytes(1, 'big')
        output += byt

    return output 

# Encrypt the data with AES 128 ECB
def aes_encrypt(bytes):

    # Setting up the key
    key = 0x01020304050607080102030405060708.to_bytes(16, 'little')
    cipher = AES.new(key, AES.MODE_ECB)

    # If not a valid block size, we pad with nullbytes. 
    if(len(bytes) % 16 != 0):

        # Rounds down to the nearest block size because of integer math
        bytes_in_data = int((len(bytes) + 16) / 16) * 16
        bytes = bytes.ljust(bytes_in_data, b"\x00")

    ciphertext = cipher.encrypt(bytes)
    return ciphertext

# Decrypt the data with AES 128 ECB
def aes_decrypt(bytes):

    # Size of the KEY determines the variation of AES to use (128, 256, etc.)
    # Had to flip this to be LITTLE instead of big when converting it. 
    key = 0x01020304050607080102030405060708.to_bytes(16, 'little')
    #key = b"1234567812345678"
    print("Key: ", key)
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = cipher.decrypt(bytes)
    return plaintext
    
'''
Takes in a hex string (without '0x' in front) and turn it into an list of bytes.

[0x0, 0x1....]
'''
def convert_hex_string_to_arr(data):
    byte_arr = []
    for index in range(0, len(data), 2):
        new_byte = data[index:index+2]
        new_byte = int(new_byte, 16)
        
        byte_arr.append(new_byte)

    return byte_arr

'''
CRC calculation happens over the size, address (not used here) and the AES encrypted payload. 
- The polynomial is ``is x^16 + x^12 + x^5 + 1``. 
- Found with ``./reveng -w 16 -s 19a5dee9d6d8180f410ccaf519827de5fbeaa1f4f570f661f8b03c0feeb452c9d096d6 199956e597f1bdb9b3938004afa057d69feaa1f4f570f661f8b03c0feeb452c9d06a31 19a5dee9d6d8180f410ccaf519827de5fbfa1067c4ed82f613993ca46bc62e40f565bf 19a5dee9d6d8180f410ccaf519827de5fbc8a049d8b04f5b733eec3d723e1e898ac065``

'''
def crc_bytes(data_input): 
    crc16 = crcmod.mkCrcFun(0x11021, initCrc=0xd9fb, xorOut=0x0000, rev=False)
    return crc16(data_input)

def decode_test():
    #input_bytes = [0x11, 0x22, 0x33, 0x44] # Test input from LFSR sheet
    #input_bytes = [0xE6, 0x22, 0x66, 0xB0, 0x61, 0x79, 0xD4, 0x2B, 0x16, 0x52 ,0x81 ,0x69 ,0x17 ,0x6B, 0x97, 0xB5, 0xD1, 0x54, 0x15, 0xEF, 0x43, 0xC0, 0xAB, 0x90, 0x1E, 0x2A, 0xDF, 0x4A, 0x13, 0x98, 0x01, 0xD1, 0xDC, 0x5C, 0x1F] # Base packet

    #input_bytes = [0xE6, 0x59, 0x75, 0x0E, 0x71, 0xC9, 0x2B, 0x79, 0xEF, 0x93, 0x9A, 0x65, 0xC2, 0xD6, 0x4D, 0xFF, 0x08, 0x54, 0x15, 0xEF, 0x43, 0xC0, 0xAB, 0x90, 0x1E, 0x2A, 0xDF, 0x4A, 0x13, 0x98, 0x01, 0xD1, 0xDC, 0xCC, 0x24]
    
    '''
    CRC is REAL weird...
    Maybe it's the data whitening? 
    This OVERFLOWS so maybe it gets reseeded? 
    From what I have tested, the NEW seed may be 0x80. This gives us BOTH the first bits of the CRC that we expect. But, to be continued!
    '''
    # From scoreboard preset base with flickering first character in Home score with 'I' in stead of H.
    # 34a5dee9d6d8180f410ccaf519827de5fb5f6c3a90a938989f8f9d4737d4cfc9194c822a420c7e15edcb666b9d984865eb83324a04e252e87ed3c66cf8ec85326cef6
    #input_bytes =  [0xCB ,0x22 ,0x66 ,0xB0 ,0x61 ,0x79 ,0xD4 ,0x2B ,0x16 ,0x52 ,0x81 ,0x69 ,0x17 ,0x6B ,0x97 ,0xB5 ,0xD1 ,0xE1 ,0xD8 ,0x21 ,0x26 ,0x19 ,0x65 ,0x69 ,0x79 ,0x15 ,0x7E ,0x02 ,0xCA ,0xF8 ,0x9C ,0xD1 ,0x15 ,0x86 ,0x4B ,0xD1 ,0x0B ,0x3B ,0x9B ,0xBD ,0xBC ,0xF0 ,0x49 ,0x0A ,0x37 ,0xEA ,0x50 ,0xE1 ,0xE9 ,0xA0 ,0x11 ,0xE1 ,0x67 ,0x6B ,0x03, 0x5B ,0x99 ,0x58 ,0xB4, 0xFC ,0xB4 ,0x04 ,0xF3 ,0x92 ,0xD9, 0xC1 ,0x86]

    # 9 Dash :) 
    # 3468e615161cd57cff2819b8a651b30d61bf4f9f4eba9238d8458c5a8f41820ae54c822a420c7e15edcb666b9d984865eb0f1d090889d9a4b4d459af920c20b9324906
    input_bytes =  [0xCB, 0xEF, 0x5E, 0x4C, 0xA1, 0xBD, 0x19, 0x58, 0xA8, 0x76, 0x52, 0x24, 0xA8, 0xB8, 0x59, 0x5D, 0x4B, 0x01, 0xFB, 0x84, 0xF8, 0x0A, 0xCF, 0xC9, 0x3E, 0xDF, 0x6F, 0x1F, 0x72, 0x6D, 0xD1, 0x12, 0xE9, 0x86, 0x4B, 0xD1, 0x0B, 0x3B, 0x9B, 0xBD, 0xBC, 0xF0, 0x49, 0x0A, 0x37, 0xEA, 0x50, 0xE1, 0xE9, 0x2C, 0x3E, 0xA2, 0x6B, 0x00, 0x88, 0x17, 0x53, 0x5F, 0x2B, 0x3F, 0xDE, 0xE4, 0xDB, 0x78, 0xCD, 0x46, 0x76]    

    # HOMI 
    #input_bytes =  [0xCB, 0x34, 0x4B, 0xCA, 0xAC, 0x6A, 0x34, 0xEF, 0xEC, 0x57, 0xAF, 0x9C, 0x43, 0x29, 0x33, 0x37, 0x9C, 0x65, 0x33, 0xAE, 0xE3, 0x4A, 0x49, 0x65, 0xF0, 0xCA, 0x13, 0x3B, 0x95, 0x91, 0xC6, 0x4C, 0x79, 0x86, 0x4B, 0xD1, 0x0B, 0x3B, 0x9B, 0xBD, 0xBC, 0xF0, 0x49, 0x0A, 0x37, 0xEA, 0x50, 0xE1, 0xE9, 0xA0, 0x11, 0xE1, 0x67, 0x6B, 0x03, 0x5B, 0x99, 0x58, 0xB4, 0xFC, 0xB4, 0x04, 0xF3, 0x92, 0xD9, 0x67, 0x49]
    output_bytes_tmp = whiten_bytes(input_bytes)
    #print(len(output_bytes))
    print("Dewhitened Bytes: ", end='')
    print_bytes(output_bytes_tmp)

    # Small vs. large packet calculations
    length = 33 if len(input_bytes) <= (32 + 1 + 2) else 65
    output_bytes = byte_arr_to_bytes(output_bytes_tmp)[1:length]

    crc_data = crc_bytes(byte_arr_to_bytes(output_bytes_tmp)[0:length])
    CRC_bytes = output_bytes_tmp[length:] # Final 2 bits
    print("CRC: Proper: ", end="")
    print_bytes(CRC_bytes)
    print("My Calc CRC:", hex(crc_data))


    #print("Decrypted Bytes: ", end='')

    data = list(aes_decrypt(output_bytes))
    print_bytes(data)
    data = data[4:]

    string = ""
    for char in data:
        string += chr(char)
    
    print(string)


def encode_test():

    input_bytes = [0x19, 0xff,0xff,0x0,0x0,0x33,0x30,0x32,0x35,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x31,0x30,0x33,0x33,0x48,0x4e,0x43,0x47]

    # Encrypt the data
    input_bytes = byte_arr_to_bytes(input_bytes)[1:] # Remove the first byte, which is for the encryption.
    ciphertext = aes_encrypt(input_bytes) # Encrypt the data
    ciphertext_lst = [0x19] + list(ciphertext) # Size needs to be included on this.
    print_bytes(ciphertext_lst)

    # Calculate the CRC
    crc_data = crc_bytes(bytearray(ciphertext_lst))
    crc_data = convert_hex_string_to_arr(hex(crc_data)[2:])

    # Whiten the data.
    white_bytes = whiten_bytes(ciphertext_lst + crc_data)
    print_bytes(white_bytes)

if __name__ == "__main__":
    #encode_test()
    decode_test()
    #brute_force_seed2()
