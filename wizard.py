# Ace_Combat_Wizard by Andrei Segal (Andrei_sgl @ Github)
# This tool is meant to replace ACAnalysis as a multi-purpose modding utility
# for Ace Combat Games.

import os
import dearpygui.dearpygui as dpg
import time

# Project opening
BASE_FOLDER = os.getcwd()
PROJECTS_BASE_FOLDER = "Projects"

CURR_PROJECT = ""

TEMPLATES_FOLDER = "Templates"

def start_gui():
    dpg.create_context()
    dpg.create_viewport(title='Ace Combat Wizard', width=600, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    current_window_tag = "mainwindow"
    with dpg.window(tag=current_window_tag):
        #dpg.add_window(label= "aaa", tag= current_window_tag)
        dpg.set_primary_window(current_window_tag, True)
        dpg.add_text("Hello, world", parent= current_window_tag)
        dpg.add_button(label="Check Projects", callback=project_checking, parent= current_window_tag)
    
    dpg.start_dearpygui()
    dpg.destroy_context()


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

def project_checking():
    # Project Checking
    current_window_tag = "project_list"
    if dpg.does_alias_exist(current_window_tag):
        dpg.remove_alias(current_window_tag)
    
    with dpg.window(tag=current_window_tag):
        #dpg.add_window(label= "aaa", tag= current_window_tag)
        
        PROJECT_LIST = os.listdir(PROJECTS_BASE_FOLDER)
        print(PROJECT_LIST)
        dpg.add_listbox(items= PROJECT_LIST, parent= current_window_tag)
        dpg.add_button(label="Create New Project", callback=project_creation_gui)


def project_creation_gui():
    # Project Creation
    current_window_tag = "create_project"
    if dpg.does_alias_exist(current_window_tag):
        dpg.remove_alias(current_window_tag)
    
    
    with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left, modal=True, tag=current_window_tag):
    
        project_info_file = ""
        project_info_list = [ ["Project name", ""] ]

        uuid_entry_list = []
        for entry in project_info_list:
            uuid_entry_list.append(dpg.add_input_text(label= entry[0]))
        
        dpg.add_button(label="Create New Project", callback=lambda: dpg.configure_item(current_window_tag, show=False))

        print("sup")

        project_name = project_info_list[0][1]
        if project_name != "":
            print("wooo")
            # Create folder for project
            project_path = PROJECTS_BASE_FOLDER + "/" + project_name
            if not os.path.exists(project_path):
                os.mkdir(project_path)
            else:
                print("Project already exists! Try another name.")
        else:
            print("nooo")



files_starter()

start_gui()


print("end")