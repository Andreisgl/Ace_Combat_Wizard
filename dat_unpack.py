'''This is a rewrite of the DAT unpacker'''
import os

def line_fill(position, line_length):
    '''This function returns the ammount of characters/bytes
    necessary to fill up the rest of the current line.'''
    aux = position % line_length
    aux = line_length - aux
    return aux



def ext_read(in_dat):
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
        ## Add back the 0 indexes
        #for zo in zero_offset_list:
        #    file_data_list.insert(zo, 0)

    return file_data_list, zero_offset_list

def ext_save(output_folder, data_list, zero_offset_list, name_list:list=[]):
    '''Saves the extracted data to a dir.
    name_list: allows non-empty files to be named'''
    
    # Create destination folder if it does not exist
    os.makedirs(name=output_folder, exist_ok=True)

    # Deal with name list
    def match_length(list1, list2):
        aux_list1 = list1[:]
        target_len = len(list2)
        if len(aux_list1) < target_len:
            aux_list1.extend([''] * (target_len - len(aux_list1)))
        elif len(aux_list1) > target_len:
            aux_list1 = aux_list1[:target_len]
        return aux_list1
    
    name_list = match_length(name_list, data_list)
    #print(name_list)
    # Join data and name lists
    data_name_list = []
    for i, name in enumerate(name_list):
        data_name_list.append([data_list[i], name])
    
    print(data_name_list)
    print('\n--------------------------------\n')


    for i, data in enumerate(data_name_list):
        prefix = str(i).zfill(len(str(abs(len(data_name_list)-1)))) # zfills index

        file_type = data[0][:3] # get first 3 letters
        if not file_type.isalnum():
            file_type = "unk"
        else:
            file_type = file_type.decode()
        
        #else:
        #    file_type = file_type.decode()
        
        file_name = data[1]
        file_name = prefix + '_' + file_type + '_' + file_name + '.subdat'
        data_name_list[i][1] = file_name

    for data in data_name_list:
        file_path = os.path.join(output_folder, data[1])
        with open(file_path, 'wb') as file:
            file.write(data[0])

    # Write zero_offset file
    zof_file_path = os.path.join(output_folder, '_zof.zof')
    with open(zof_file_path, 'w') as zof_file:
        zof_file.writelines([str(x) for x in zero_offset_list])




in_file = os.path.join('testfolder', 'out', '0251.dat')

data_list, zero_off_list = ext_read(in_file)
o_folder = 'test_out_dat'
ext_save(o_folder, data_list, zero_off_list)

##

rep_in_folder = o_folder
rep_out_file = os.path.join('testfolder', 'repack_out', 'new_0251.dat')



rep_read(rep_in_folder)