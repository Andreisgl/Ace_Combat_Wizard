'''Ace Combat Wizard by Andrei Segal (Andreisgl @ Github, SegalAndrei @ Twitter)
With code by Death_the_d0g (deaththed0g @ Github, Death_the_d0g @ Twitter)

This script is intended to simplify the modding process of Ace Combat 5/Zero
It unites and automates the basic unpacking tools
to speed up the modding process.'''

import os
from asset_classes import Container

class Project():
    def __init__(self, project_folder_path:str, create_project:bool = False):
        self.project_name = ''




        print('--- Ace Combat Wizard ---')

        if create_project:
            print('Creating project:')
            answer = input('Choose a name for the new project: ')
            self.project_name = answer


        


        self._folders_list = []
        self._project_folder_path = project_folder_path

        self.is_project_new = False
        self._flag_file_path = os.path.join(self._project_folder_path, 'project.ACW')

       


        if not os.path.isfile(self._flag_file_path):
            self.is_project_new = True
            print('Creating project:')
            answer = input('Choose a name for the new project: ')
            self.project_name = answer
            with open(self._flag_file_path, 'w') as file:
                file.write(f'project_name: {answer}')
        else:
            self.is_project_new = False
            print('Opening project:')
            answer = input('Choose a name for the new project: ')
            with open(self._flag_file_path, 'w') as file:
                file.write(f'project_name: {answer}')

        self._source_folder = os.path.join(project_folder_path, 'source')
        self._folders_list.append(self._source_folder)

        for folder in self._folders_list:
            os.makedirs(folder)



def main():
    #cwd = os.path.dirname(__file__)
    #projects_folder = os.path.join(cwd, 'projects')

    DATA_PAC_path = 'DATA.PAC'
    DATA_TBL_path = 'DATA.TBL'

    Container()

if __name__ == '__main__':
    main()
