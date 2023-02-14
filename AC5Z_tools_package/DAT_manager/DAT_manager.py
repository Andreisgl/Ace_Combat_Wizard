# This module is responsible for extracting and rebuilding .DAT files.
# Code based on the .DAT scripts
# by Death_the_d0g (deaththed0g @ Github, Death_the_d0g @ Twitter) and
# Andrei Segal (Andreisgl @ Github, SegalAndrei @ Twitter)

import os
import re

CURRENT_PROJECT_PATH = ""
DAT_MANAGER_FOLDER = "DAT_Manager_data"
ZERO_OFFSET_FOLDER = "zof"

def check_main_folders(current_project_path):
    global CURRENT_PROJECT_PATH
    global ZERO_OFFSET_FOLDER
    global DAT_MANAGER_FOLDER
    CURRENT_PROJECT_PATH = current_project_path

    DAT_MANAGER_FOLDER = os.path.join(CURRENT_PROJECT_PATH, DAT_MANAGER_FOLDER)
    ZERO_OFFSET_FOLDER = os.path.join(DAT_MANAGER_FOLDER, ZERO_OFFSET_FOLDER)
    
    if not os.path.isdir(DAT_MANAGER_FOLDER):
        os.mkdir(DAT_MANAGER_FOLDER)
    if not os.path.isdir(ZERO_OFFSET_FOLDER):
        os.mkdir(ZERO_OFFSET_FOLDER)
    pass

def extract(dat):
    # Receives BufferedRead of .dat file,
    # returns list of streams and names for each file.
    
    file_data_list = []
    file_name_list = []
    #type 2 extraction:
    offset_list = []
    zero_offset_list = []
    number_of_files = int.from_bytes(dat.read(4), byteorder = "little")
    aux = (number_of_files + 1) * 4
    header_length = line_fill(aux, 16)
    header_length += aux

    for offset in range(number_of_files):
        data = dat.read(4)
        if data == b'\x00\x00\x00\x00':
            zero_offset_list.append(offset)
        else:
            offset_list.append(int.from_bytes(data, "little"))
    # Add false last index to read last file
    dat.seek(0, 2)
    offset_list.append(dat.tell())

    zof_name = os.path.basename(dat.name).split('.')[0]
    pass_to_zof(zero_offset_list, zof_name, ZERO_OFFSET_FOLDER)
    
    
    dat.seek(offset_list[0], 0)
    for index in range(len(offset_list) -1):
        read_size = offset_list[index+1] - offset_list[index]
        file_data_list.append(dat.read(read_size))

    for index in range(len(file_data_list)):
        extension = file_data_list[index][:3]
        if not extension.isalnum():
            extension = "unk"
        else:
            extension = extension.decode()
        extension = "." + extension

        file_name = (str(index).zfill(4)) + extension
        file_name_list.append(file_name)

    return(file_data_list, file_name_list)

def line_fill(position, line_length):
    # This function returns the ammount of characters/bytes
    # necessary to fill up the rest of the current line.
    aux = position % line_length
    aux = line_length - aux
    return aux

def pass_to_zof(zof_list, file_name , zof_folder):
    zof_extension = ".zof"
    file_name = file_name+zof_extension
    file_path = os.path.join(zof_folder, file_name)
    with open(file_path, "wb") as zof:
        for index in zof_list:
            zof.write(index.to_bytes(4, "little"))
