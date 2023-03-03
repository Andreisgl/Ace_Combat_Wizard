# Ace Combat Wizard by Andrei Segal (Andreisgl @ Github, SegalAndrei @ Twitter)
# With code by Death_the_d0g (deaththed0g @ Github, Death_the_d0g @ Twitter)

# This script is intended to simplify the modding process of Ace Combat 5/Zero
# It unites and automates the basic unpacking tools
# to speed up the modding process.

import os
import shutil


EXE_ROOT = ".\\"
PROJECTS_FOLDER = "PROJECTS"
CURRENT_PROJECT_PATH = ""
CURRENT_PROJECT_ROOT_PATH = "root"

PAC_name = "DATA.PAC"
TBL_name = "DATA.TBL"

# PROJECT INITIALIZING SECTION ------------------------------------

def check_main_folders():
    # Check if all core folders are present.
    # Returns "True" if there are projects present. "False" if not.
    # If there are no projects, create one immediately.
    global PROJECTS_FOLDER
    PROJECTS_FOLDER = os.path.join(EXE_ROOT, PROJECTS_FOLDER)
    
    if not os.path.isdir(PROJECTS_FOLDER):
        os.mkdir(PROJECTS_FOLDER)
    if not len(os.listdir(PROJECTS_FOLDER)):
        print("NO PROJECTS FOUND!")
        new_project_name = input("Enter new project's name: ")
        os.mkdir(os.path.join(PROJECTS_FOLDER, new_project_name))
        open_project(os.path.join(PROJECTS_FOLDER, new_project_name))
        return False
    return True

def open_project_prompt():
    # Prompts the user to choose a project from PROJECTS_FOLDER.
    print("Choose a project:\n")
    project_list = os.listdir(PROJECTS_FOLDER)
    for index in range(len(project_list)):
        print(str(index) + " - " + project_list[index] + "\n")
    
    can_repeat = True
    while can_repeat:
        try:
            answer = int(input("Select project index: "))
        except ValueError:
            continue
        
        #if not isinstance(answer, int):
        #    continue
        if answer not in range(len(project_list)):
            continue
        
        next_project = project_list[answer]
        print("Opening: " + next_project)

        open_project(os.path.join(PROJECTS_FOLDER, next_project))
        can_repeat = False

def check_project_folders(project_path):
    global CURRENT_PROJECT_ROOT_PATH
    CURRENT_PROJECT_ROOT_PATH = os.path.join(CURRENT_PROJECT_PATH, CURRENT_PROJECT_ROOT_PATH)
    if not os.path.isdir(CURRENT_PROJECT_ROOT_PATH):
        os.mkdir(CURRENT_PROJECT_ROOT_PATH)

def check_project_files(project_path):
    global PAC_name
    global TBL_name

    global PAC_path
    global TBL_path
    PAC_path = os.path.join(CURRENT_PROJECT_ROOT_PATH, PAC_name)
    TBL_path = os.path.join(CURRENT_PROJECT_ROOT_PATH, TBL_name)
    #if not os.path.isfile(PAC_path):
    #    return False
    #if not os.path.isfile(TBL_path):
    #    return False
        
    return True

def open_project(project_path):
    # Opens a project from its path.
    global CURRENT_PROJECT_PATH
    CURRENT_PROJECT_PATH = project_path
    check_project_folders(project_path)
    
    if not check_project_files(project_path):
        print("Either DATA.PAC or DATA.TBL missing!")

if check_main_folders():
    open_project_prompt()

# END PROJECT INITIALIZING SECTION ------------------------------------  


# PAC MANIPULATION SECTION ------------------------------------
import AC5Z_tools_package.PAC_manager.PAC_manager as PAC_manager

def extract_PAC_data(pac_path, tbl_path):
    # Gets data from DATA.PAC file and replaces it with a folder
    # with its extracted .dat contents.
    DAT_file_data_list = []
    DAT_file_name_list = []
    with open(pac_path, 'rb') as pac:
        with open(tbl_path, 'rb') as tbl:
            DAT_file_data_list, DAT_file_name_list = PAC_manager.extraction(pac, tbl)
    
    os.remove(pac_path)
    os.mkdir(pac_path)
    for index in range(len(DAT_file_data_list)):
        file_path = os.path.join(pac_path, DAT_file_name_list[index])
        with open(file_path, 'wb') as file:
            file.write(DAT_file_data_list[index])
        
def rebuild_PAC_data(pac_path, tbl_path):
    # Sends a list of all .DAT's streams to package,
    # gets a new .TBL file and reassembles .PAC file in-function.
    # Removes DATA.PAC folder and replaces it with new DATA.PAC file.
    dat_list = os.listdir(pac_path)
    dat_data_list = []
    tbl_data_list = []
    tbl_data = b''
    pac_data = b''
    for index in range(len(dat_list)):
        dat_list[index] = os.path.join(pac_path, dat_list[index])
        with open(dat_list[index], "rb") as file:
            dat_data_list.append(file.read())

    pac_data, tbl_data_list = PAC_manager.rebuilding(dat_data_list)

    shutil.rmtree(pac_path)
    
    with open(pac_path, "wb") as pac:
            pac.write(pac_data)
    with open(tbl_path, "wb") as tbl:
        for data in tbl_data_list:
            tbl.write(data)

#extract_PAC_data(PAC_path, TBL_path)
#rebuild_PAC_data(PAC_path, TBL_path)

# END PAC MANIPULATION SECTION ------------------------------------


# DAT MANIPULATION SECTION ------------------------------------
import AC5Z_tools_package.DAT_manager.DAT_manager as DAT_manager
DAT_manager.check_main_folders(CURRENT_PROJECT_PATH)

def extract_DAT_data(dat_file_path):
    subdat_data_list = []
    subdat_name_list = []

    with open(dat_file_path, "rb") as dat:
        subdat_data_list, subdat_name_list = DAT_manager.extract(dat)
        pass

    os.remove(dat_file_path)
    os.mkdir(dat_file_path)
    for index in range(len(subdat_data_list)):
        file_path = os.path.join(dat_file_path, subdat_name_list[index])
        with open(file_path, 'wb') as file:
            file.write(subdat_data_list[index])

def repack_DAT_data(dat_file_path):
    ### repack (will become a function later)

    repacked_dat = DAT_manager.repack(dat_file_path)
    shutil.rmtree(dat_file_path)
    with open(dat_file_path, 'wb') as dat:
        dat.write(repacked_dat)


def list_all_paths_in_dir(base_dir):
    # Store all available .dat files.

    # Can cover all files, will do only 251 to 281, the missions.
    dat_file_name_list = os.listdir(base_dir)
    file_path_list = dat_file_name_list
    for index in range(len(file_path_list)):
        file_path_list[index] = os.path.join(base_dir, file_path_list[index])
    #return file_path_list
    
    # return files in

    #dat_file_path = file_path_list[251]
    #return file_path_list[251:282]

    interval = file_path_list[251:282]
    return interval


def extract_all_DATs(DAT_dir):
    path_list = list_all_paths_in_dir(DAT_dir)
    if len(path_list) == 1:
        extract_DAT_data(path_list[0])
    else:
        for path in path_list:
            extract_DAT_data(path)
    pass

def repack_all_DATs(DAT_dir):
    path_list = list_all_paths_in_dir(DAT_dir)
    if len(path_list) == 1:
        repack_DAT_data(path_list[0])
    else:
        for path in path_list:
            repack_DAT_data(path)
    pass


#extract_all_DATs(PAC_path)
#repack_all_DATs(PAC_path)

# END DAT MANIPULATION SECTION ------------------------------------


# FULL MANIPULATION
def total_unpack():
    extract_PAC_data(PAC_path, TBL_path)
    extract_all_DATs(PAC_path)

def total_repack():
    repack_all_DATs(PAC_path)
    rebuild_PAC_data(PAC_path, TBL_path)
# END FULL MANIPULATION


# ACTUAL INTERFACE

print("Unpack or Repack?\n")
print("0 - UNPACK\n1 - REPACK")


while True:
    answer = int(input("Enter index: "))
    
    if answer == 0:
        total_unpack()
    elif answer == 1:
        total_repack()
    else:
        continue
    break

#extract_all_DATs(PAC_path)

# END ACTUAL INTERFACE


pass