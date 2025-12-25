'''Ace Combat Wizard by Andrei Segal (Andreisgl @ Github, SegalAndrei @ Twitter)
With code by Death_the_d0g (deaththed0g @ Github, Death_the_d0g @ Twitter)

This script is intended to simplify the modding process of Ace Combat 5/Zero
It unites and automates the basic unpacking tools
to speed up the modding process.'''

import os
import csv


def load_csv_data(file_path: str) -> list[dict] | None:
    '''
    loads a .csv file and returns a dict list
    '''
    
    # Verifica se o arquivo existe antes de tentar abri-lo.
    if not os.path.isfile(file_path):
        print(f"Erro: Arquivo CSV não encontrado em '{file_path}'")
        return None

    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8', newline='') as csvfile:
            # csv.DictReader trata a primeira linha como cabeçalho automaticamente.
            # Ele já retorna um iterador de dicionários, exatamente o que queremos.
            reader = csv.DictReader(csvfile)
            
            # Converte o iterador para uma lista.
            data = list(reader)
            
            # Opcional: Imprime uma confirmação de sucesso.
            print(f"Sucesso: {len(data)} linhas de dados carregadas de '{os.path.basename(file_path)}'.")

    except FileNotFoundError:
        # Esta verificação é redundante devido ao os.path.isfile, mas é uma boa prática.
        print(f"Erro: Arquivo CSV não encontrado em '{file_path}'")
        return None
    except Exception as e:
        # Captura outros erros potenciais (problemas de permissão, codificação, etc.)
        print(f"Ocorreu um erro ao ler o arquivo CSV '{file_path}': {e}")
        return None
        
    return data


def get_tool(search):
    ''' A placeholder method to fetch a tool based on the preset data.'''

    pac_mng_path = os.path.join(TOOLS_PACK_FOLDER, 'PAC_manager', 'PAC_manager.py')
    dat_mng_path = os.path.join(TOOLS_PACK_FOLDER, 'DAT_manager', 'DAT_manager.py')
    
    if search == 'PAC_manager':
        return pac_mng_path
    elif search == 'DAT_manager':
        return dat_mng_path
    else:
        return None

def prepare_files(folder_path:str):
    '''Takes all files from a folder and decides what is a preset and what is not.'''
    game_files = []
    preset_files = []
    preset_file = ''
    
    for file in os.listdir(PROJECT_FOLDER):
        if os.path.splitext(file)[1] == '.preset':
            preset_files.append(file)
        else:
            game_files.append(file)

    # There must be only one preset file. Consider the first one only.
    if len(preset_file) >= 1:
        preset_file = preset_file[0]
    else:
        preset_file = None
    
    game_files = [os.path.join(folder_path, x) for x in game_files]
    preset_file = os.path.join(folder_path, preset_files[0])
    return game_files, preset_file






PROJECT_FOLDER = os.path.join('.', 'tool', 'testproject')
NAMEMAPS_FOLDER = os.path.join('.', 'tool', 'name_maps')
TOOLS_PACK_FOLDER = os.path.join('.', 'AC5Z_tools_package')



contents, ROOT_PRESET_PATH = prepare_files(PROJECT_FOLDER)


#ROOT_PRESET_PATH = os.path.join(PROJECT_FOLDER, 'root.preset')




preset_data = load_csv_data(ROOT_PRESET_PATH)




pass