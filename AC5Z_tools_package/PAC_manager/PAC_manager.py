# This module is responsible for extracting and rebuilding .PAC files.
# Code based on the "ACZ_PAC_TOOLS.2" by Death_the_d0g (deaththed0g @ Github, Death_the_d0g @ Twitter)

import argparse as argp
import os

def unpack(pac_path, tbl_path):
    with open(tbl_path, 'rb') as tbl_file:
        val = 0
        f_n = 0
        f_offset = 8
        offset_list = []
        size_list = []
        file_data_list = []
        file_name_list = []

        tbl_file.seek(0, 0)
        tbl_nof = int.from_bytes(tbl_file.read(4), byteorder = "little")
        for f in range(tbl_nof):
            tbl_file.seek(f_offset, 0)
            offset_list.append(int.from_bytes(tbl_file.read(4), byteorder = "little"))
            f_offset = f_offset + 4
            tbl_file.seek(f_offset, 0)
            size_list.append(int.from_bytes(tbl_file.read(4), byteorder = "little"))
            f_offset = f_offset + 4
    with open(pac_path, 'rb') as pac_file:
        for f in range(tbl_nof):
            file_name_list.append(str(f).zfill(4) + ".dat")

            pac_file.seek(offset_list[val])
            data = pac_file.read(size_list[val])
            file_data_list.append(data)

            print("file:", file_name_list[f], "offset:", hex(offset_list[val]), "size:", size_list[val])
            val = val + 1
            #f_n = f_n + 1
    return file_data_list, file_name_list

def rebuilding(dat_data_list):
    print("Building DATA.TBL")
    tbl_data_list = []
    
    # Add header
    true_nof = len(dat_data_list)
    pad = 0
    true_nof_hex = true_nof.to_bytes(4, "little")
    pad_hex = pad.to_bytes(4, "little")
    tbl_data_list.append(true_nof_hex)
    tbl_data_list.append(pad_hex)
    # Rest of the data
    offset = 0
    for file in dat_data_list:
        # TBL:
        size = len(file)
        tbl_data_list.append(offset.to_bytes(4, "little"))
        tbl_data_list.append(size.to_bytes(4, "little"))
        offset = offset + size
    final_TBL_data = b''.join(tbl_data_list)    

    print("Building DATA.PAC")
    final_PAC_data = b''.join(dat_data_list)

    return final_PAC_data, final_TBL_data

###

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
    parser = argp.ArgumentParser()
    parser.add_argument("mode")
    parser.add_argument("input_path")
    parser.add_argument("output_path")
    try:
        args = parser.parse_args()
    except:
        print('Uncaught exception!')
        input('Press Enter to exit...')
    print(args)
    
    arg_mode_options = ['extract', 'rebuild']
    arg_path_types = ['folder', 'file']
    argcheck_return = argcheck(args, arg_mode_options, arg_path_types)
    
    if not argcheck_return:
        print('paths failed check!')
        input('Press Enter to exit...')
        return False
    else:
        print('paths are valid!')
    
    ## Apply args
    #if args.mode






if __name__ == '__main__':
    main()