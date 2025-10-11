'''This is a rewrite of the DAT unpacker'''
import os
import argparse as argp

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




'''
# Unpack routine
in_file = os.path.join('testfolder', 'out', '0251.dat')

data_list, zero_off_list = ext_read(in_file)
o_folder = 'test_out_dat'
ext_save(o_folder, data_list, zero_off_list)
'''

##


def rep_read(in_folder, out_file):
    file_name_list = os.listdir(in_folder)
    file_path_list = [os.path.join(in_folder, x) for x in file_name_list]
    #number_of_files = len(file_name_list)
    zero_offset_file = ''

    zof_found = False
    for i, f in enumerate(file_path_list):    
        file, extension = os.path.splitext(f)
        if extension == '.zof':
            zof_found = True
            zero_offset_file = f
            
            # Remove '.zof' from lists
            file_path_list.pop(i)
            file_name_list.pop(i)
            break
    
    if not zof_found:
        input('.zof file not found!!\nPress Enter to exit...')
        exit(1)
    
    # Read '.zof' file
    zero_offset_list = []
    with open(zero_offset_file, 'r') as zof:
        zero_offset_list = zof.readlines()[:]
        zero_offset_list = [int(x) for x in zero_offset_list]
     
    header_contents = []

    offset_acc = 0
    for subdat in file_path_list:
        header_contents.append(offset_acc)
        size = os.path.getsize(subdat)
        offset_acc += size

    #
    
    header_length = ((len(header_contents) + len(zero_offset_list)) * 4) # Number of instances in header
    header_length += line_fill(header_length, 16) # Pad header to fit in 16 byte lines

    # Add header length to header contents:
    header_contents = [x+header_length for x in header_contents]

    # Add back the 0 indexes
    for zo in zero_offset_list:
        header_contents.insert(zo, 0)

        
    header_contents.insert(0, len(header_contents)) # Insert 'nof' as first number


    # Write output .dat file
    dir = os.path.dirname(out_file)
    os.makedirs(dir, exist_ok=True)
    with open(out_file, 'wb') as out_dat:
        # Write header
        for pos in header_contents:
            data = pos.to_bytes(4, "little")
            out_dat.write(data)
        
        # Write file data
        for file in file_path_list:
            with open(file, 'rb') as subdat:
                out_dat.write(subdat.read())
    pass


'''
# Repack routine
rep_in_folder = o_folder
rep_out_file = os.path.join('testfolder', 'repack_out', 'new_0251.dat')

rep_read(rep_in_folder, rep_out_file)
'''


def argcheck(args, mode_options, path_types):
    # Argument validation    
    while True:
        # Check mode
        if not args.mode in mode_options:
            print(f'Argument *mode* is invalid!')
            print(f'Valid options: {mode_options}')
            input('Press any key to exit')
            break
        print('mode is valid!')
        
        # Check paths
        invalid_path_flag = False
        #
        input_shouldbedir = False
        output_shouldbedir = False
        if args.mode == 'extract':
            input_shouldbedir = False
            output_shouldbedir = True
        else:
            input_shouldbedir = True
            output_shouldbedir = False

        paths = ((args.input_path, input_shouldbedir), (args.output_path, output_shouldbedir))
        

        for path in paths:
            if not os.path.exists(path[0]):
                if path[1] and args.mode=='extract':
                    os.makedirs(path[0])
                elif (not path[1]) and args.mode=='repack':
                    pass # Repack mode and output_file does not exist yet
                else:
                    print(f'Path {path[0]} is not valid!')
                    invalid_path_flag = True
                    break
            
            if not os.path.isdir(path[0]) == path[1]:
                typestring = path_types[0]
                if not path[1]:
                    typestring = path_types[1]
                print(f'Path {path[0]} must be a {typestring}')
                invalid_path_flag = True
            
        if invalid_path_flag:
            return False
        
        return True

def main():
    # Argument parsing

    arg_mode_options = ['extract', 'repack']
    arg_path_types = ['folder', 'file']
    
    


    parser = argp.ArgumentParser()
    parser.add_argument("mode", help=f'options: {arg_mode_options}')
    parser.add_argument("input_path")
    parser.add_argument("output_path")
    try:
        args = parser.parse_args()
    except:
        print('Uncaught exception!')
        input('Press Enter to exit...')
        #exit(1)
        return
    print(args)
    

    argcheck_return = argcheck(args, arg_mode_options, arg_path_types)


    if not argcheck_return:
        print('paths failed check!')
        input('Press Enter to exit...')
        return False
    else:
        print('paths are valid!')
    
    ## Apply args
    if args.mode == 'extract':
        print(f'extracting... in:{args.input_path} to {args.output_path}')
        # Assumes TBL has the same name as PAC
        TBL_path = ((args.input_path).split('.')[0]) + '.TBL'
        unpack_pac(args.input_path, TBL_path, args.output_path) 

    elif args.mode == 'repack':
        print(f'rebuilding... in:{args.input_path} to {args.output_path}')
        # Open folder, extract data.
        # output_data = rebuild(data)
        # Save output_data
        repack_pac(args.input_path, args.output_path)
        
    else:
        print('Invalid mode entry!')
        input('Press Enter to exit...')






if __name__ == '__main__':
    main()

