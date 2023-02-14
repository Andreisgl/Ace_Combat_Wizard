# Ace Combat Wizard by Andrei Segal (Andreisgl @ Github, SegalAndrei @ Twitter)
# With code by Death_the_d0g (deaththed0g @ Github, Death_the_d0g @ Twitter)

# This script is intended to simplify the modding process of Ace Combat 5/Zero
# It unites and automates the basic unpacking tools
# to speed up the modding process.

import os


EXE_ROOT = ".\\"
PROJECTS_FOLDER = "PROJECTS"
CURRENT_PROJECT_PATH = ""
CURRENT_PROJECT_ROOT_PATH = "root"

PAC_name = "DATA.PAC"
TBL_name = "DATA.TBL"

# PROJECT INITIALIZING FUNCTIONS ------------------------------------

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

    PAC = os.path.join(CURRENT_PROJECT_ROOT_PATH, PAC_name)
    TBL = os.path.join(CURRENT_PROJECT_ROOT_PATH, TBL_name)
    if not os.path.isfile(PAC):
        return False
    if not os.path.isfile(TBL):
        return False
        
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
# END PROJECT INITIALIZING FUNCTIONS ------------------------------------  


# File manipulation functions ------------------------------------






print("end")