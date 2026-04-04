'''Ace Combat Wizard by Andrei Segal (Andreisgl @ Github, SegalAndrei @ Twitter)
With code by Death_the_d0g (deaththed0g @ Github, Death_the_d0g @ Twitter)

This script is intended to simplify the modding process of Ace Combat 5/Zero
It unites and automates the basic unpacking tools
to speed up the modding process.'''

import os
import json
from asset_classes import Container

class Project():
    def __init__(self, project_folder_path:str, name:str=''):
        '''Class that represents a ACW project.
        - name: If creating a new project, this will be its name.
            If project already exists, this will be unused.'''
    
        # Project preparation
        self.project_name = ''
        self._folders_list = []
        #self._files_list = []
        self._project_folder_path = project_folder_path
        self._flag_file_path = os.path.join(self._project_folder_path, 'project.ACW')
        #
        self._source_folder = os.path.join(project_folder_path, 'source')
        self._folders_list.append(self._source_folder)
        # Creates folders if they don't exist. If they do, ignore.
        for folder in self._folders_list:
            os.makedirs(folder, exist_ok=True)

        # Check for ACW file. Create if non-existent.
        if os.path.exists(self._flag_file_path): # Read project name from .ACW
            data = ''
            with open(self._flag_file_path, 'r') as flag_file:
                data = json.load(flag_file)
            self.project_name = data['project_name']
        else: # Create ACW flag file and write the project's name to it.
            self.project_name = name
            data = {'project_name': self.project_name}
            with open(self._flag_file_path, 'w') as flag_file:
                json.dump(data, flag_file)
        
        # Check for game data
        if len(os.listdir(self._source_folder)) <= 0:
            print('No game files!') # Source is empty
        
        

        
       



def main():
    print('--- Ace Combat Wizard ---')
    cwd = os.path.dirname(__file__)
    projects_folder = os.path.join(cwd, 'projects')

    DATA_PAC_path = 'DATA.PAC'
    DATA_TBL_path = 'DATA.TBL'

    os.makedirs(projects_folder, exist_ok=True)

    project_path = os.path.join(projects_folder, 'testproj')
    current_project = Project(project_folder_path=project_path, name='test_proj')
    pass

if __name__ == '__main__':
    main()
