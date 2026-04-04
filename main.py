'''Ace Combat Wizard by Andrei Segal (Andreisgl @ Github, SegalAndrei @ Twitter)
With code by Death_the_d0g (deaththed0g @ Github, Death_the_d0g @ Twitter)

This script is intended to simplify the modding process of Ace Combat 5/Zero
It unites and automates the basic unpacking tools
to speed up the modding process.'''

import os
import json
from asset_classes import Container, Asset, DataRefPac, DataRefTbl, DataPacAsset, DatMission

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
        
class ACZProject(Project):
    '''Extends class 'Project for ACZ-specific projects.'''
    def __init__(self, project_folder_path:str, name:str=''):
        super().__init__(project_folder_path=project_folder_path, name=name)
        #
        
        # References setup:
        tbl_path = os.path.join(self._source_folder, 'DATA.TBL')
        pac_path = os.path.join(self._source_folder, 'DATA.PAC')

        raw_datapac_data = b''
        with open(pac_path, 'rb') as file:
            raw_datapac_data = file.read()
        
        raw_datatbl_data = b''
        with open(tbl_path, 'rb') as file:
            raw_datatbl_data = file.read()
            
        self.DATA_TBL_REF = DataRefTbl(name='datatbl_ref', raw_data=raw_datatbl_data)
        self.DATA_PAC_REF = DataRefPac(name='datapac_ref', raw_data=raw_datapac_data, tbl_ref=self.DATA_TBL_REF)

        # Asset creation:
        self.DATA_PAC = DataPacAsset(name='DATA.PAC', size=os.stat(pac_path).st_size, offset = 0, data_ref=self.DATA_PAC_REF, index=0)

        self.DAT_ASSET_LIST = {
            '251': {'dat_type': 'mission', 'name': 'Glacial Skies', 'ace_style': 'all'},
            '252': {'dat_type': 'mission', 'name': 'Annex', 'ace_style': 'all'},
            '253': {'dat_type': 'mission', 'name': 'The Round Table', 'ace_style': 'M'},
            '254': {'dat_type': 'mission', 'name': 'The Round Table', 'ace_style': 'S'},
            '255': {'dat_type': 'mission', 'name': 'The Round Table', 'ace_style': 'K'},
            '256': {'dat_type': 'mission', 'name': 'Juggernaut', 'ace_style': 'M'},
            '257': {'dat_type': 'mission', 'name': 'Juggernaut', 'ace_style': 'S'},
            '258': {'dat_type': 'mission', 'name': 'Juggernaut', 'ace_style': 'K'},
            '259': {'dat_type': 'mission', 'name': 'Flicker of Hope', 'ace_style': 'all'},
            '260': {'dat_type': 'mission', 'name': 'Diapason', 'ace_style': 'all'},
            '261': {'dat_type': 'mission', 'name': 'Bastion', 'ace_style': 'all'},
            '262': {'dat_type': 'mission', 'name': 'Merlon', 'ace_style': 'M'},
            '263': {'dat_type': 'mission', 'name': 'Merlon', 'ace_style': 'S'},
            '264': {'dat_type': 'mission', 'name': 'Merlon', 'ace_style': 'K'},
            '265': {'dat_type': 'mission', 'name': 'Sword of Annihilation', 'ace_style': 'all'},
            '266': {'dat_type': 'mission', 'name': 'Mayhem', 'ace_style': 'M'},
            '267': {'dat_type': 'mission', 'name': 'Mayhem', 'ace_style': 'S'},
            '268': {'dat_type': 'mission', 'name': 'Mayhem', 'ace_style': 'K'},
            '269': {'dat_type': 'mission', 'name': 'The Inferno', 'ace_style': 'all'},
            '270': {'dat_type': 'mission', 'name': 'The Stage of the Apocalypse', 'ace_style': 'all'},
            '271': {'dat_type': 'mission', 'name': 'Lying in Deceit', 'ace_style': 'all'},
            '272': {'dat_type': 'mission', 'name': 'The Final Overture', 'ace_style': 'M'},
            '273': {'dat_type': 'mission', 'name': 'The Final Overture', 'ace_style': 'S'},
            '274': {'dat_type': 'mission', 'name': 'The Final Overture', 'ace_style': 'K'},
            '275': {'dat_type': 'mission', 'name': 'The Talon of Ruin', 'ace_style': 'all'},
            '276': {'dat_type': 'mission', 'name': 'The Demon of the Round Table', 'ace_style': 'M'},
            '277': {'dat_type': 'mission', 'name': 'The Demon of the Round Table', 'ace_style': 'S'},
            '278': {'dat_type': 'mission', 'name': 'The Demon of the Round Table', 'ace_style': 'K'},
            '279': {'dat_type': 'mission', 'name': 'The Valley of Kings', 'ace_style': 'all'},
            '280': {'dat_type': 'mission', 'name': 'ZERO', 'ace_style': 'all'},
            '281': {'dat_type': 'mission', 'name': 'The Gauntlet', 'ace_style': 'all'}
        }

        #
        for dat_index in self.DAT_ASSET_LIST:
            raw_asset:Asset
            raw_asset = self.DATA_PAC.children[int(dat_index)]
            entry = self.DAT_ASSET_LIST[dat_index]
            new_child = None
            
            dat_type = entry['dat_type']
            new_name = f'{dat_type}_{entry['name']}'
            
            if entry['dat_type'] == 'mission':
                ace_style = entry['ace_style']
                new_child = DatMission(name=new_name, size=-1, offset=-1, data_ref=self.DATA_PAC.data_ref, index=int(dat_index), ace_style=ace_style, deferred_children=True)
                self.DATA_PAC.generate_child(index=int(dat_index), obj=new_child) # TODO: Consider making this line for all asset types
            #elif .... other classes...

            


            #DATA_PAC.generate_child(int(dat_index), new_name, child_class)
            #DATA_PAC.generate_child(int(dat_index), new_name, child_class)

            print(self.DATA_PAC.children[int(dat_index)])

        pass
        


        
       



def main():
    print('--- Ace Combat Wizard ---')
    cwd = os.path.dirname(__file__)
    projects_folder = os.path.join(cwd, 'projects')

    #DATA_PAC_path = 'DATA.PAC'
    #DATA_TBL_path = 'DATA.TBL'

    os.makedirs(projects_folder, exist_ok=True)

    project_path = os.path.join(projects_folder, 'testproj')
    current_project = ACZProject(project_folder_path=project_path, name='test_proj')







    pass

if __name__ == '__main__':
    main()
