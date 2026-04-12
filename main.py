'''Ace Combat Wizard by Andrei Segal (Andreisgl @ Github, SegalAndrei @ Twitter)
With code by Death_the_d0g (deaththed0g @ Github, Death_the_d0g @ Twitter)

This script is intended to simplify the modding process of Ace Combat 5/Zero
It unites and automates the basic unpacking tools
to speed up the modding process.'''

import os

from asset_classes import Container, Asset, DataRefPac, DataRefTbl, DataPacAsset, DatMission, Project, ACZProject



        
       



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
