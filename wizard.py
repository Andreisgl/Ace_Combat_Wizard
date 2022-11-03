# Ace_Combat_Wizard by Andrei Segal (Andrei_sgl @ Github)
# This tool is meant to replace ACAnalysis as a multi-purpose modding utility
# for Ace Combat Games.

import os

# Project opening
BASE_FOLDER = os.getcwd()
PROJECTS_BASE_FOLDER = "Projects"

CURR_PROJECT = ""

TEMPLATES_FOLDER = "Templates"

def files_starter():
    # Makes sure all necessary files and folders for startup are present
    global PROJECTS_BASE_FOLDER
    PROJECTS_BASE_FOLDER = BASE_FOLDER + "/" + PROJECTS_BASE_FOLDER
    if not os.path.exists(PROJECTS_BASE_FOLDER):
        os.mkdir(PROJECTS_BASE_FOLDER)

    global TEMPLATES_FOLDER
    TEMPLATES_FOLDER = BASE_FOLDER + "/" + TEMPLATES_FOLDER
    if not os.path.exists(TEMPLATES_FOLDER):
        os.mkdir(TEMPLATES_FOLDER)

files_starter()

# Project Opening