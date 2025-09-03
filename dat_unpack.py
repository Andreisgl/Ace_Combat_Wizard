'''This is a rewrite of the DAT unpacker'''
import os

def line_fill(position, line_length):
    '''This function returns the ammount of characters/bytes
    necessary to fill up the rest of the current line.'''
    aux = position % line_length
    aux = line_length - aux
    return aux

in_dat = os.path.join('testfolder', 'out', '0251.dat')

#print(os.listdir(in_dat))

with open(in_dat, 'rb') as file:
    # Read header
    read = file.read(4)
    number_of_files = int.from_bytes(read, byteorder = "little")
    aux = (number_of_files + 1) * 4
    header_length = aux + line_fill(aux, 16)
    #
    offset_list = [] # Contains non-zero header entries
    zero_offset_list = [] # Contains index of header entries that are 0
    for offset in range(number_of_files):
        data = file.read(4)
        data = int.from_bytes(data, byteorder = "little")
        if data != 0:
            offset_list.append(data)
        else:
            zero_offset_list.append(offset)
    print(offset_list)
    print(zero_offset_list)

    # Read data from offsets
    file_data_list = []
    for i in range(len(offset_list)):
        next_i = i+1
        if next_i < len(offset_list): # If index is not the last:
            size = offset_list[next_i] - offset_list[i]
            data = file.read(size)
        else: # If index is the last one, read to the end of the file
            data = file.read()
            
        file_data_list.append(data)
    # Add back the 0 indexes
    for zo in zero_offset_list:
        file_data_list.insert(zo, 0)

    pass
    







