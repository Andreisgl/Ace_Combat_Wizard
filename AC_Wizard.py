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
        answer = int(input("Select project index: "))
        
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


# PAC manipulation section ------------------------------------
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
        
        with open(os.path.join(pac_path, DAT_file_name_list[index] ), 'wb') as file:
            file.write(DAT_file_data_list[index])
        
def rebuild_PAC_data(pac_path, tbl_path):
    dat_list = os.listdir(pac_path)
    dat_data_list = []
    tbl_data_list = []
    for index in range(len(dat_list)):
        dat_list[index] = os.path.join(pac_path, dat_list[index])
        with open(dat_list[index], "rb") as file:
            dat_data_list.append(file.read())

    tbl_data_list = PAC_manager.rebuilding(dat_data_list)

    shutil.rmtree(pac_path)
    
    with open(pac_path, "wb") as pac:
        for file in dat_data_list: 
            pac.write(file)
    with open(tbl_path, "wb") as tbl:
        for data in tbl_data_list:
            tbl.write(data)


#extract_PAC_data(PAC_path, TBL_path)
rebuild_PAC_data(PAC_path, TBL_path)






print("end")