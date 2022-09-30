'''
Basic analysis of the data. 
Including frequency information, bit changes and things. 
'''

from os import listdir
from os.path import isfile, join
from lfsr import whiten_bytes, print_bytes, byte_arr_to_bytes, aes_decrypt, aes_encrypt, crc_bytes, convert_hex_string_to_arr

def modify_file(filename):

    f = open("recordings/" + filename)
    old_data = f.readline()
    f.close()

    # Adding the raw binary format
    data = old_data.replace(",", "").replace("\n","")
    raw_binary = data.replace(" ", "")
    raw_binary = raw_binary.replace("\n", "")
    
    # Adding the hex format
    full_hex_output = ""
    for index in range(0, int(len(raw_binary)), 4):
        binary_group = raw_binary[index:index+4]
        hex_output = int(binary_group,2)
        full_hex_output += hex(hex_output)[2:].capitalize() + " "

    ''' Convert to ASCII
    for index in range(int(len(raw_binary)/8) - 8): 
        binary_group = raw_binary[index*8:index*8 +8]
        hex_output = int(binary_group,2)
        byte_number = hex_output.bit_length() + 7
        binary_array = hex_output.to_bytes(byte_number, "big")
        ascii_text = binary_array.decode()
        print(ascii_text)
    '''
    # Write the material
    f = open("recordings/" + filename, "w")
    f.write(old_data)
    f.write(raw_binary + '\n') 
    f.write(full_hex_output)
    f.write("\n")
    f.close()

'''
Go from binary 0s and 1s to hex.
'''
def add_formats():

    # Change of the writable files
    onlyfiles = [f for f in listdir("./recordings/") if(isfile(join("./recordings/", f)) and f.endswith(".txt") )]

    for elt in onlyfiles:
        modify_file(elt)

'''
Read the information from the file, given the file name. 
Returns data in the format below:
- original format of 0s and 1s, (0, 1, 0,...)
- Full binary format (010101010) 
- Hex (AAAAA)
'''
def open_file(filename):
    f = open("./recordings/" + filename)
    old_data = f.readline().replace("\n", "")
    raw_binary = f.readline().replace("\n", "")
    raw_hex = f.readline().replace("\n", "").replace(" ", "")
    return old_data, raw_binary, raw_hex

'''
Returns a dictionary of all of the captures put into three formats: 
- 0: Raw 0's and 1's
- 1: Raw hex (0-9, A-F) 
- 2: The original format from inspectrum

The key is the name of the file minus the '.txt'
'''
def get_all_content():
    onlyfiles = [f for f in listdir("./recordings/") if(isfile(join("./recordings/", f)) and f.endswith(".txt") )]

    content = {}
    for elt in onlyfiles:
        data = open_file(elt)    
        content[elt.replace(".txt","")] = [data[1], data[2], data[0]]
    return content

'''
Given a two strings of binary bits, compare them.
'''
def comp(content_dict, input1, input2):
    print("Compare: ", input1  + ',' + input2)
    data1 = content_dict[input1][0]
    data2 = content_dict[input2][0]

    missed_list = []
    hit_list = []
    for index in range(len(data1) if len(data1) < len(data2) else len(data2)):
        bit1 = data1[index]
        bit2 = data2[index]

        # Hits and misses
        if(bit1 == bit2):
            hit_list.append(index)
        else: 
            missed_list.append(index)
    
    return hit_list, missed_list

'''
Find amount of preamble bytes
'''
def check_preamble(content):
    if(type(content) == list):
        content = content[0]
    
    counter = 0
    for index in range(0, len(content), 2):
        sequence = content[index:index + 2] 
        if(sequence == "10"):
            counter += 1
        else: 
            break 

    return counter

'''
Find first diff compared to base for calls files
'''
def compare_all(content):
    smallest_index = 100000
    for elt in content: 
        if(elt == 'Base'):
            continue
        results = comp(content, 'Base', elt) # Lists inside a list
        if(len(results[1]) == 0 ):
            print("Completely Similar!", elt) 
            continue
        print(results[1][0], elt) 
        if(results[1] != [] and results[1][0] < smallest_index):
            smallest_index = results[1][0]

'''
The point I realized that ECB AES was being used. 

The first check differences START at 60 and mostly stop at 188-320. This is 128 bits! 
The second check differences start at 320ish. 

These groups of 128-bits and complete lack of other correlation made it obvious that AES CBC was being used.
'''
def show_ECB_diff():
    content = get_all_content()
    print(comp(content, "Base", "ShotClock29")[1])
    print(comp(content, "Base", "GuestFoul2")[1])


def convert_for_operation(entry, payload_size=32):
    hex_data = entry[1] # Check out the check representation of the data
    data = hex_data.split('2DD4') # Find the sync word. Removes it as well.
    if(len(data) == 1):
        print("No sync word found!")
        return False 

    data = data[1]

    # First byte is the LENGTH 
    # Bytes 1-33 are encrypted 
    # Bytes 34-35 are the CRC
    length = data[0:2]

    # Payload
    encrypted_payload = data[2:(payload_size*2)+2]

    # Right after the payload
    crc = data[(payload_size * 2) + 2:(payload_size * 2) + 6]

    # Convert the output to an array of bytes for each item
    return [convert_hex_string_to_arr(length), convert_hex_string_to_arr(encrypted_payload), convert_hex_string_to_arr(crc)]

def payload_divided_content():
    content = get_all_content()
    
    '''
    Dictionary of the following format: 
    - key: Name of the file. For instance, 'Base'. 
    - Value - list:
        - Size byte. In the form of an list. 
        - Encrypted payload bytes. Each byte is an entry in the list. 
        - CRC. Each byte is an entry in the list. 

    '''
    split_content = {}
    output = convert_for_operation(content['Base'])

    
    for element in content:
        output = convert_for_operation(content[element])
        if(output != False):
            split_content[element] = output
    
    return split_content

def crc_whiten_test():

    content = payload_divided_content()
    base = content['Base']
    whitened_bytes = whiten_bytes(base[0] + base[1] + base[2])
    print_bytes(whitened_bytes)
    print_bytes(whitened_bytes[0:33])

    #byte_data = byte_arr_to_bytes(whitened_bytes)[0:33]
    print(hex(crc_bytes(bytearray(whitened_bytes[0:33]))))

    data = ""
    for byte in whitened_bytes:
        data += "0x{:02x}".format(byte)[2:]

if __name__ == "__main__":
    # Update file information (binary to hex info)
    add_formats()


    content = get_all_content()
    print(content)
    #print(content['DashTo9PresetMode'][1])

    '''
    print(comp(content, "Custom57GameClock", "GameClock2457")[1])

    print(content['Custom57GameClock'][0][213:])
    print(content['GameClock2457'][0][213:])

    print(content["Custom57GameClock"][1][int(316/4):])
    print(content["GameClock2457"][1][int(316/4):])
    #print(comp(content, "GameClock2457", "GuestFoul2")[1])
    #show_ECB_diff()
    # Show the ECB difference
    #show_ECB_diff()
    '''
