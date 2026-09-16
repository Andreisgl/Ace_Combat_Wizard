''' Classes for common assets. '''
import os
import json


class Project():
    ACW_FILENAME = 'project.ACW'

    def __init__(self, project_folder_path:str, name:str='', game_id:str=''):
        '''Class that represents a ACW project.
        - name: If creating a new project, this will be its name.
            If project already exists, this will be unused.
        - game_id: If creating a new project, the game this project is for
            (see game_registry.GAME_REGISTRY). If the project already exists,
            this is unused - the game id is read back from project.ACW instead.'''

        # Project preparation
        self.project_name = ''
        self.game_id = game_id
        self._folders_list = []
        #self._files_list = []
        self._project_folder_path = project_folder_path
        self._flag_file_path = os.path.join(self._project_folder_path, self.ACW_FILENAME)
        #
        self._source_folder = os.path.join(project_folder_path, 'source')
        self._folders_list.append(self._source_folder)
        # Creates folders if they don't exist. If they do, ignore.
        for folder in self._folders_list:
            os.makedirs(folder, exist_ok=True)

        # Check for ACW file. Create if non-existent.
        if os.path.exists(self._flag_file_path): # Read project name/game from .ACW
            data = ''
            with open(self._flag_file_path, 'r') as flag_file:
                data = json.load(flag_file)
            self.project_name = data['project_name']
            self.game_id = data['game']
        else: # Create ACW flag file and write the project's name/game to it.
            self.project_name = name
            data = {'project_name': self.project_name, 'game': self.game_id}
            with open(self._flag_file_path, 'w') as flag_file:
                json.dump(data, flag_file)

        # Check for game data
        if len(os.listdir(self._source_folder)) <= 0:
            print('No game files!') # Source is empty

        # Per-class asset tables for this game/project (e.g. {DatStage: ...}).
        # Populated by subclasses (ACZProject, and eventually an AC5Project)
        # with their own game-specific tables under the same class keys, so
        # Container instances can look theirs up automatically regardless of
        # which game is actually loaded - see Asset.root_project and
        # Container._resolve_asset_table.
        self.asset_tables: dict = {}

    @property
    def folder_path(self) -> str:
        '''This project's root folder on disk - used by game_registry's
        Save As (duplicate_project) to copy the folder without reaching
        into the underscore-prefixed attribute from outside this class.'''
        return self._project_folder_path

    def get_asset_table(self, asset_class) -> dict | None:
        '''Returns the asset table registered for `asset_class` in this
        project, or None if this project doesn't define one for it.'''
        return self.asset_tables.get(asset_class)

    @staticmethod
    def read_acw_metadata(project_folder_path:str) -> dict | None:
        '''Reads project.ACW from `project_folder_path` without constructing
        a Project - used to peek at a candidate folder's metadata (project
        name, game id) before knowing which Project subclass to instantiate,
        e.g. game_registry.open_project() and the project picker's folder
        listing. Returns None if there's no valid project.ACW there.'''
        flag_file_path = os.path.join(project_folder_path, Project.ACW_FILENAME)
        if not os.path.isfile(flag_file_path):
            return None
        try:
            with open(flag_file_path, 'r') as flag_file:
                return json.load(flag_file)
        except (json.JSONDecodeError, OSError):
            return None

class ACZProject(Project):
    '''Extends class 'Project for ACZ-specific projects.'''
    GAME_ID = 'ACZ'
    DISPLAY_NAME = 'Ace Combat Zero'
    REQUIRED_SOURCE_FILES = ('DATA.PAC', 'DATA.TBL')

    def __init__(self, project_folder_path:str, name:str=''):
        super().__init__(project_folder_path=project_folder_path, name=name, game_id=self.GAME_ID)
        
        # References setup:
        tbl_path = os.path.join(self._source_folder, 'DATA.TBL')
        pac_path = os.path.join(self._source_folder, 'DATA.PAC')

        raw_datapac_data = b''
        with open(pac_path, 'rb') as file:
            raw_datapac_data = file.read()
        
        raw_datatbl_data = b''
        with open(tbl_path, 'rb') as file:
            raw_datatbl_data = file.read()
            
        self._DATA_TBL_REF = DataRefTbl(name='datatbl_ref', raw_data=raw_datatbl_data)
        self._DATA_PAC_REF = DataRefPac(name='datapac_ref', raw_data=raw_datapac_data, tbl_ref=self._DATA_TBL_REF)

        

        # Slot contents sourced from death_the_d0g's DATA.PAC content listing
        # for SLUS21346 ("ACZ_makepack_contents_SLUS21346.txt"). Ace-style
        # (M/S/K) ordering for entries below is preserved as originally
        # authored in this table; see the '[CONFIRM ACE STYLE]' tag added in
        # Container.generate_children() - the source doc's own ordering isn't
        # fully self-consistent (e.g. it lists Juggernaut as S/M/K, not M/S/K
        # as below), so none of it is trusted blindly without a manual check
        # against other sources (dialogue, etc).
        self.ACZ_DAT_ASSET_LIST = {
            '3': {'type': 'stage_dat', 'name': 'Glacial Skies', 'ace_style': ''},
            '4': {'type': 'stage_dat', 'name': 'Annex', 'ace_style': ''},
            '5': {'type': 'stage_dat', 'name': 'The Round Table', 'ace_style': 'M'},
            '6': {'type': 'stage_dat', 'name': 'The Round Table', 'ace_style': 'S'},
            '7': {'type': 'stage_dat', 'name': 'The Round Table', 'ace_style': 'K'},
            '8': {'type': 'stage_dat', 'name': 'Juggernaut', 'ace_style': 'M'},
            '9': {'type': 'stage_dat', 'name': 'Juggernaut', 'ace_style': 'S'},
            '10': {'type': 'stage_dat', 'name': 'Juggernaut', 'ace_style': 'K'},
            '11': {'type': 'stage_dat', 'name': 'Flicker of Hope', 'ace_style': ''},
            '12': {'type': 'stage_dat', 'name': 'Diapason', 'ace_style': ''},
            '13': {'type': 'stage_dat', 'name': 'Bastion', 'ace_style': ''},
            '14': {'type': 'stage_dat', 'name': 'Merlon', 'ace_style': 'M'},
            '15': {'type': 'stage_dat', 'name': 'Merlon', 'ace_style': 'S'},
            '16': {'type': 'stage_dat', 'name': 'Merlon', 'ace_style': 'K'},
            '17': {'type': 'stage_dat', 'name': 'Sword of Annihilation', 'ace_style': ''},
            '18': {'type': 'stage_dat', 'name': 'Mayhem', 'ace_style': 'M'},
            '19': {'type': 'stage_dat', 'name': 'Mayhem', 'ace_style': 'S'},
            '20': {'type': 'stage_dat', 'name': 'Mayhem', 'ace_style': 'K'},
            '21': {'type': 'stage_dat', 'name': 'The Inferno', 'ace_style': ''},
            '22': {'type': 'stage_dat', 'name': 'The Stage of the Apocalypse', 'ace_style': ''},
            '23': {'type': 'stage_dat', 'name': 'Lying in Deceit', 'ace_style': ''},
            '24': {'type': 'stage_dat', 'name': 'The Final Overture', 'ace_style': 'M'},
            '25': {'type': 'stage_dat', 'name': 'The Final Overture', 'ace_style': 'S'},
            '26': {'type': 'stage_dat', 'name': 'The Final Overture', 'ace_style': 'K'},
            '27': {'type': 'stage_dat', 'name': 'The Talon of Ruin', 'ace_style': ''},
            '28': {'type': 'stage_dat', 'name': 'The Demon of the Round Table', 'ace_style': 'M'},
            '29': {'type': 'stage_dat', 'name': 'The Demon of the Round Table', 'ace_style': 'S'},
            '30': {'type': 'stage_dat', 'name': 'The Demon of the Round Table', 'ace_style': 'K'},
            '31': {'type': 'stage_dat', 'name': 'The Valley of Kings', 'ace_style': ''},
            '32': {'type': 'stage_dat', 'name': 'ZERO', 'ace_style': ''},
            '33': {'type': 'stage_dat', 'name': 'The Gauntlet', 'ace_style': ''},
            #
            '43': {'type': 'stage_dat', 'name': 'Valais Air Force Base', 'ace_style': ''},
            #
            # Multiplayer stages (recycled from AC5, per the doc's own notes).
            '49': {'type': 'stage_dat', 'name': 'Multiplayer Stage 1 (AC5 OP KATINA LIFELINE DAY)', 'ace_style': ''},
            '50': {'type': 'stage_dat', 'name': 'Multiplayer Stage 2 (AC5 VLADIMIR MOUNTAINS)', 'ace_style': ''},
            '51': {'type': 'stage_dat', 'name': 'Multiplayer Stage 3 (AC5 BANA CITY)', 'ace_style': ''},
            '52': {'type': 'stage_dat', 'name': 'Multiplayer Stage 4 (AC5 SOLO ISLANDS)', 'ace_style': ''},
            '53': {'type': 'stage_dat', 'name': 'Multiplayer Stage 5 (AREA B7R)', 'ace_style': ''},
            '54': {'type': 'stage_dat', 'name': 'Multiplayer Stage 6 (AC5 GHOSTS OF RAZGRIZ CANYON)', 'ace_style': ''},
            '55': {'type': 'stage_dat', 'name': 'Multiplayer Stage (AC5 OP KATINA STONEHENGE, UNUSED)', 'ace_style': ''},
            '56': {'type': 'stage_dat', 'name': 'Multiplayer Stage 7 (AC5 OP KATINA ARCHIPIELAGO)', 'ace_style': ''},
            '57': {'type': 'stage_dat', 'name': 'Multiplayer Stage (AC5 AKERSON HILL, UNUSED)', 'ace_style': ''},
            '58': {'type': 'stage_dat', 'name': 'Multiplayer Stage (AC5 SEA OF CHAOS, UNUSED)', 'ace_style': ''},
            #
            # Second, exact-duplicate 31-stage block ("Free Mission" - assumed
            # to be the series' usual non-story replay mode, matching this
            # game's structurally-identical stage_dat files).
            '81': {'type': 'stage_dat', 'name': 'Glacial Skies (Free Mission)', 'ace_style': ''},
            '82': {'type': 'stage_dat', 'name': 'Annex (Free Mission)', 'ace_style': ''},
            '83': {'type': 'stage_dat', 'name': 'The Round Table (Free Mission)', 'ace_style': 'M'},
            '84': {'type': 'stage_dat', 'name': 'The Round Table (Free Mission)', 'ace_style': 'S'},
            '85': {'type': 'stage_dat', 'name': 'The Round Table (Free Mission)', 'ace_style': 'K'},
            '86': {'type': 'stage_dat', 'name': 'Juggernaut (Free Mission)', 'ace_style': 'S'},
            '87': {'type': 'stage_dat', 'name': 'Juggernaut (Free Mission)', 'ace_style': 'M'},
            '88': {'type': 'stage_dat', 'name': 'Juggernaut (Free Mission)', 'ace_style': 'K'},
            '89': {'type': 'stage_dat', 'name': 'Flicker of Hope (Free Mission)', 'ace_style': ''},
            '90': {'type': 'stage_dat', 'name': 'Diapason (Free Mission)', 'ace_style': ''},
            '91': {'type': 'stage_dat', 'name': 'Bastion (Free Mission)', 'ace_style': ''},
            '92': {'type': 'stage_dat', 'name': 'Merlon (Free Mission)', 'ace_style': 'M'},
            '93': {'type': 'stage_dat', 'name': 'Merlon (Free Mission)', 'ace_style': 'S'},
            '94': {'type': 'stage_dat', 'name': 'Merlon (Free Mission)', 'ace_style': 'K'},
            '95': {'type': 'stage_dat', 'name': 'Sword of Annihilation (Free Mission)', 'ace_style': ''},
            '96': {'type': 'stage_dat', 'name': 'Mayhem (Free Mission)', 'ace_style': 'M'},
            '97': {'type': 'stage_dat', 'name': 'Mayhem (Free Mission)', 'ace_style': 'S'},
            '98': {'type': 'stage_dat', 'name': 'Mayhem (Free Mission)', 'ace_style': 'K'},
            '99': {'type': 'stage_dat', 'name': 'The Inferno (Free Mission)', 'ace_style': ''},
            '100': {'type': 'stage_dat', 'name': 'The Stage of the Apocalypse (Free Mission)', 'ace_style': ''},
            '101': {'type': 'stage_dat', 'name': 'Lying in Deceit (Free Mission)', 'ace_style': ''},
            '102': {'type': 'stage_dat', 'name': 'The Final Overture (Free Mission)', 'ace_style': 'M'},
            '103': {'type': 'stage_dat', 'name': 'The Final Overture (Free Mission)', 'ace_style': 'S'},
            '104': {'type': 'stage_dat', 'name': 'The Final Overture (Free Mission)', 'ace_style': 'K'},
            '105': {'type': 'stage_dat', 'name': 'The Talon of Ruin (Free Mission)', 'ace_style': ''},
            '106': {'type': 'stage_dat', 'name': 'The Demon of the Round Table (Free Mission)', 'ace_style': 'M'},
            '107': {'type': 'stage_dat', 'name': 'The Demon of the Round Table (Free Mission)', 'ace_style': 'S'},
            '108': {'type': 'stage_dat', 'name': 'The Demon of the Round Table (Free Mission)', 'ace_style': 'K'},
            '109': {'type': 'stage_dat', 'name': 'The Valley of Kings (Free Mission)', 'ace_style': ''},
            '110': {'type': 'stage_dat', 'name': 'ZERO (Free Mission)', 'ace_style': ''},
            '111': {'type': 'stage_dat', 'name': 'The Gauntlet (Free Mission)', 'ace_style': ''},
            #
            '251': {'type': 'mission_dat', 'name': 'Glacial Skies', 'ace_style': ''},
            '252': {'type': 'mission_dat', 'name': 'Annex', 'ace_style': ''},
            '253': {'type': 'mission_dat', 'name': 'The Round Table', 'ace_style': 'M'},
            '254': {'type': 'mission_dat', 'name': 'The Round Table', 'ace_style': 'S'},
            '255': {'type': 'mission_dat', 'name': 'The Round Table', 'ace_style': 'K'},
            '256': {'type': 'mission_dat', 'name': 'Juggernaut', 'ace_style': 'M'},
            '257': {'type': 'mission_dat', 'name': 'Juggernaut', 'ace_style': 'S'},
            '258': {'type': 'mission_dat', 'name': 'Juggernaut', 'ace_style': 'K'},
            '259': {'type': 'mission_dat', 'name': 'Flicker of Hope', 'ace_style': ''},
            '260': {'type': 'mission_dat', 'name': 'Diapason', 'ace_style': ''},
            '261': {'type': 'mission_dat', 'name': 'Bastion', 'ace_style': ''},
            '262': {'type': 'mission_dat', 'name': 'Merlon', 'ace_style': 'M'},
            '263': {'type': 'mission_dat', 'name': 'Merlon', 'ace_style': 'S'},
            '264': {'type': 'mission_dat', 'name': 'Merlon', 'ace_style': 'K'},
            '265': {'type': 'mission_dat', 'name': 'Sword of Annihilation', 'ace_style': ''},
            '266': {'type': 'mission_dat', 'name': 'Mayhem', 'ace_style': 'M'},
            '267': {'type': 'mission_dat', 'name': 'Mayhem', 'ace_style': 'S'},
            '268': {'type': 'mission_dat', 'name': 'Mayhem', 'ace_style': 'K'},
            '269': {'type': 'mission_dat', 'name': 'The Inferno', 'ace_style': ''},
            '270': {'type': 'mission_dat', 'name': 'The Stage of the Apocalypse', 'ace_style': ''},
            '271': {'type': 'mission_dat', 'name': 'Lying in Deceit', 'ace_style': ''},
            '272': {'type': 'mission_dat', 'name': 'The Final Overture', 'ace_style': 'M'},
            '273': {'type': 'mission_dat', 'name': 'The Final Overture', 'ace_style': 'S'},
            '274': {'type': 'mission_dat', 'name': 'The Final Overture', 'ace_style': 'K'},
            '275': {'type': 'mission_dat', 'name': 'The Talon of Ruin', 'ace_style': ''},
            '276': {'type': 'mission_dat', 'name': 'The Demon of the Round Table', 'ace_style': 'M'},
            '277': {'type': 'mission_dat', 'name': 'The Demon of the Round Table', 'ace_style': 'S'},
            '278': {'type': 'mission_dat', 'name': 'The Demon of the Round Table', 'ace_style': 'K'},
            '279': {'type': 'mission_dat', 'name': 'The Valley of Kings', 'ace_style': ''},
            '280': {'type': 'mission_dat', 'name': 'ZERO', 'ace_style': ''},
            '281': {'type': 'mission_dat', 'name': 'The Gauntlet', 'ace_style': ''},
            #
            # Multiplayer missions - mirrors the multiplayer stage block above.
            '297': {'type': 'mission_dat', 'name': 'Multiplayer Mission 1 (AC5 OP KATINA LIFELINE DAY)', 'ace_style': ''},
            '298': {'type': 'mission_dat', 'name': 'Multiplayer Mission 2 (AC5 VLADIMIR MOUNTAINS)', 'ace_style': ''},
            '299': {'type': 'mission_dat', 'name': 'Multiplayer Mission 3 (AC5 BANA CITY)', 'ace_style': ''},
            '300': {'type': 'mission_dat', 'name': 'Multiplayer Mission 4 (AC5 SOLO ISLANDS)', 'ace_style': ''},
            '301': {'type': 'mission_dat', 'name': 'Multiplayer Mission 5 (AREA B7R)', 'ace_style': ''},
            '302': {'type': 'mission_dat', 'name': 'Multiplayer Mission 6 (AC5 GHOSTS OF RAZGRIZ CANYON)', 'ace_style': ''},
            '303': {'type': 'mission_dat', 'name': 'Multiplayer Mission (AC5 OP KATINA STONEHENGE, UNUSED)', 'ace_style': ''},
            '304': {'type': 'mission_dat', 'name': 'Multiplayer Mission 7 (AC5 OP KATINA ARCHIPIELAGO)', 'ace_style': ''},
            '305': {'type': 'mission_dat', 'name': 'Multiplayer Mission (AC5 AKERSON HILL, UNUSED)', 'ace_style': ''},
            '306': {'type': 'mission_dat', 'name': 'Multiplayer Mission (AC5 SEA OF CHAOS, UNUSED)', 'ace_style': ''},
            #
            # Free Flight files - same 31 stages as the story block, again.
            '329': {'type': 'free_flight_dat', 'name': 'Glacial Skies', 'ace_style': ''},
            '330': {'type': 'free_flight_dat', 'name': 'Annex', 'ace_style': ''},
            '331': {'type': 'free_flight_dat', 'name': 'The Round Table', 'ace_style': 'M'},
            '332': {'type': 'free_flight_dat', 'name': 'The Round Table', 'ace_style': 'S'},
            '333': {'type': 'free_flight_dat', 'name': 'The Round Table', 'ace_style': 'K'},
            '334': {'type': 'free_flight_dat', 'name': 'Juggernaut', 'ace_style': 'S'},
            '335': {'type': 'free_flight_dat', 'name': 'Juggernaut', 'ace_style': 'M'},
            '336': {'type': 'free_flight_dat', 'name': 'Juggernaut', 'ace_style': 'K'},
            '337': {'type': 'free_flight_dat', 'name': 'Flicker of Hope', 'ace_style': ''},
            '338': {'type': 'free_flight_dat', 'name': 'Diapason', 'ace_style': ''},
            '339': {'type': 'free_flight_dat', 'name': 'Bastion', 'ace_style': ''},
            '340': {'type': 'free_flight_dat', 'name': 'Merlon', 'ace_style': 'M'},
            '341': {'type': 'free_flight_dat', 'name': 'Merlon', 'ace_style': 'S'},
            '342': {'type': 'free_flight_dat', 'name': 'Merlon', 'ace_style': 'K'},
            '343': {'type': 'free_flight_dat', 'name': 'Sword of Annihilation', 'ace_style': ''},
            '344': {'type': 'free_flight_dat', 'name': 'Mayhem', 'ace_style': 'M'},
            '345': {'type': 'free_flight_dat', 'name': 'Mayhem', 'ace_style': 'S'},
            '346': {'type': 'free_flight_dat', 'name': 'Mayhem', 'ace_style': 'K'},
            '347': {'type': 'free_flight_dat', 'name': 'The Inferno', 'ace_style': ''},
            '348': {'type': 'free_flight_dat', 'name': 'The Stage of the Apocalypse', 'ace_style': ''},
            '349': {'type': 'free_flight_dat', 'name': 'Lying in Deceit', 'ace_style': ''},
            '350': {'type': 'free_flight_dat', 'name': 'The Final Overture', 'ace_style': 'M'},
            '351': {'type': 'free_flight_dat', 'name': 'The Final Overture', 'ace_style': 'S'},
            '352': {'type': 'free_flight_dat', 'name': 'The Final Overture', 'ace_style': 'K'},
            '353': {'type': 'free_flight_dat', 'name': 'The Talon of Ruin', 'ace_style': ''},
            '354': {'type': 'free_flight_dat', 'name': 'The Demon of the Round Table', 'ace_style': 'M'},
            '355': {'type': 'free_flight_dat', 'name': 'The Demon of the Round Table', 'ace_style': 'S'},
            '356': {'type': 'free_flight_dat', 'name': 'The Demon of the Round Table', 'ace_style': 'K'},
            '357': {'type': 'free_flight_dat', 'name': 'The Valley of Kings', 'ace_style': ''},
            '358': {'type': 'free_flight_dat', 'name': 'ZERO', 'ace_style': ''},
            '359': {'type': 'free_flight_dat', 'name': 'The Gauntlet', 'ace_style': ''},
            #
            # Aircraft - 36 airframes x 5 unlockable skin tiers (STANDARD/
            # MERCENARY/SOLDIER/SPECIAL/KNIGHT). Each slot is individually and
            # unambiguously labeled in the source doc (unlike stage M/S/K),
            # so the tier/callsign tag is embedded directly in the name
            # rather than needing a separate ace_style-style field/warning.
            '498': {'type': 'aircraft_dat', 'name': 'J35J Draken (STANDARD)'},
            '499': {'type': 'aircraft_dat', 'name': 'Gripen C (STANDARD)'},
            '500': {'type': 'aircraft_dat', 'name': 'Typhoon (STANDARD)'},
            '501': {'type': 'aircraft_dat', 'name': 'Tornado GR4 (STANDARD)'},
            '502': {'type': 'aircraft_dat', 'name': 'F-4E II Phantom (STANDARD)'},
            '503': {'type': 'aircraft_dat', 'name': 'F-15C Eagle -CIPHER- (STANDARD)'},
            '504': {'type': 'aircraft_dat', 'name': 'F-15 Strike Eagle (STANDARD)'},
            '505': {'type': 'aircraft_dat', 'name': 'F-15 SMTD (STANDARD)'},
            '506': {'type': 'aircraft_dat', 'name': 'FA-18C Hornet (STANDARD)'},
            '507': {'type': 'aircraft_dat', 'name': 'EA-18G (STANDARD)'},
            '508': {'type': 'aircraft_dat', 'name': 'F-16C Fighting Falcon (STANDARD)'},
            '509': {'type': 'aircraft_dat', 'name': 'F-16 XL (STANDARD)'},
            '510': {'type': 'aircraft_dat', 'name': 'F-117A Nighthawk (STANDARD)'},
            '511': {'type': 'aircraft_dat', 'name': 'FA-22A Raptor (STANDARD)'},
            '512': {'type': 'aircraft_dat', 'name': 'F-35C (STANDARD)'},
            '513': {'type': 'aircraft_dat', 'name': 'F-5E Tiger II (STANDARD)'},
            '514': {'type': 'aircraft_dat', 'name': 'F-20A Tigershark (STANDARD)'},
            '515': {'type': 'aircraft_dat', 'name': 'X-29A (STANDARD)'},
            '516': {'type': 'aircraft_dat', 'name': 'F-14D Super Tomcat (STANDARD)'},
            '517': {'type': 'aircraft_dat', 'name': 'YF-23A Black Widow II (STANDARD)'},
            '518': {'type': 'aircraft_dat', 'name': 'EA-6B Prowler (STANDARD)'},
            '519': {'type': 'aircraft_dat', 'name': 'A-10A Thunderbolt II (STANDARD)'},
            '520': {'type': 'aircraft_dat', 'name': 'Mirage 2000D (STANDARD)'},
            '521': {'type': 'aircraft_dat', 'name': 'Rafale M (STANDARD)'},
            '522': {'type': 'aircraft_dat', 'name': 'Su-27 Flanker (STANDARD)'},
            '523': {'type': 'aircraft_dat', 'name': 'Su-32 Super Flanker (STANDARD)'},
            '524': {'type': 'aircraft_dat', 'name': 'Su-37 Terminator (STANDARD)'},
            '525': {'type': 'aircraft_dat', 'name': 'Su-47 Berkut (STANDARD)'},
            '526': {'type': 'aircraft_dat', 'name': 'MiG-21bis Fishbed (STANDARD)'},
            '527': {'type': 'aircraft_dat', 'name': 'MiG-29A Fulcrum (STANDARD)'},
            '528': {'type': 'aircraft_dat', 'name': 'MiG-31 Foxhound (STANDARD)'},
            '529': {'type': 'aircraft_dat', 'name': 'F1 (STANDARD)'},
            '530': {'type': 'aircraft_dat', 'name': 'F-2A (STANDARD)'},
            '531': {'type': 'aircraft_dat', 'name': 'X-02 Wyvern (STANDARD)'},
            '532': {'type': 'aircraft_dat', 'name': 'ADF-01 Falken (STANDARD)'},
            '533': {'type': 'aircraft_dat', 'name': 'ADFX-01 Morgan (STANDARD)'},
            '534': {'type': 'aircraft_dat', 'name': 'J35J Draken (MERCENARY)'},
            '535': {'type': 'aircraft_dat', 'name': 'Gripen C (MERCENARY)'},
            '536': {'type': 'aircraft_dat', 'name': 'Typhoon (MERCENARY)'},
            '537': {'type': 'aircraft_dat', 'name': 'Tornado GR4 (MERCENARY)'},
            '538': {'type': 'aircraft_dat', 'name': 'F-4E II Phantom (MERCENARY)'},
            '539': {'type': 'aircraft_dat', 'name': 'F-15C Eagle (MERCENARY)'},
            '540': {'type': 'aircraft_dat', 'name': 'F-15 Strike Eagle (MERCENARY)'},
            '541': {'type': 'aircraft_dat', 'name': 'F-15 SMTD (MERCENARY)'},
            '542': {'type': 'aircraft_dat', 'name': 'FA-18C Hornet (MERCENARY)'},
            '543': {'type': 'aircraft_dat', 'name': 'EA-18G (MERCENARY)'},
            '544': {'type': 'aircraft_dat', 'name': 'F-16C Fighting Falcon (MERCENARY)'},
            '545': {'type': 'aircraft_dat', 'name': 'F-16 XL (MERCENARY)'},
            '546': {'type': 'aircraft_dat', 'name': 'F-117A Nighthawk (MERCENARY)'},
            '547': {'type': 'aircraft_dat', 'name': 'FA-22A Raptor (MERCENARY)'},
            '548': {'type': 'aircraft_dat', 'name': 'F-35C (MERCENARY)'},
            '549': {'type': 'aircraft_dat', 'name': 'F-5E Tiger II (MERCENARY)'},
            '550': {'type': 'aircraft_dat', 'name': 'F-20A Tigershark (MERCENARY)'},
            '551': {'type': 'aircraft_dat', 'name': 'X-29A (MERCENARY)'},
            '552': {'type': 'aircraft_dat', 'name': 'F-14D Super Tomcat (MERCENARY)'},
            '553': {'type': 'aircraft_dat', 'name': 'YF-23A Black Widow II (MERCENARY)'},
            '554': {'type': 'aircraft_dat', 'name': 'EA-6B Prowler (MERCENARY)'},
            '555': {'type': 'aircraft_dat', 'name': 'A-10A Thunderbolt II (MERCENARY)'},
            '556': {'type': 'aircraft_dat', 'name': 'Mirage 2000D (MERCENARY)'},
            '557': {'type': 'aircraft_dat', 'name': 'Rafale M (MERCENARY)'},
            '558': {'type': 'aircraft_dat', 'name': 'Su-27 Flanker (MERCENARY)'},
            '559': {'type': 'aircraft_dat', 'name': 'Su-32 Super Flanker (MERCENARY)'},
            '560': {'type': 'aircraft_dat', 'name': 'Su-37 Terminator -YELLOW- (MERCENARY)'},
            '561': {'type': 'aircraft_dat', 'name': 'Su-47 Berkut (MERCENARY)'},
            '562': {'type': 'aircraft_dat', 'name': 'MiG-21bis Fishbed (MERCENARY)'},
            '563': {'type': 'aircraft_dat', 'name': 'MiG-29A Fulcrum (MERCENARY)'},
            '564': {'type': 'aircraft_dat', 'name': 'MiG-31 Foxhound (MERCENARY)'},
            '565': {'type': 'aircraft_dat', 'name': 'F1 (MERCENARY)'},
            '566': {'type': 'aircraft_dat', 'name': 'F-2A (MERCENARY)'},
            '567': {'type': 'aircraft_dat', 'name': 'X-02 Wyvern (MERCENARY)'},
            '568': {'type': 'aircraft_dat', 'name': 'ADF-01 Falken (MERCENARY)'},
            '569': {'type': 'aircraft_dat', 'name': 'ADFX-01 Morgan (MERCENARY)'},
            '570': {'type': 'aircraft_dat', 'name': 'J35J Draken (SOLDIER)'},
            '571': {'type': 'aircraft_dat', 'name': 'Gripen C (SOLDIER)'},
            '572': {'type': 'aircraft_dat', 'name': 'Typhoon (SOLDIER)'},
            '573': {'type': 'aircraft_dat', 'name': 'Tornado GR4 (SOLDIER)'},
            '574': {'type': 'aircraft_dat', 'name': 'F-4E II Phantom (SOLDIER)'},
            '575': {'type': 'aircraft_dat', 'name': 'F-15C Eagle (SOLDIER)'},
            '576': {'type': 'aircraft_dat', 'name': 'F-15 Strike Eagle (SOLDIER)'},
            '577': {'type': 'aircraft_dat', 'name': 'F-15 SMTD (SOLDIER)'},
            '578': {'type': 'aircraft_dat', 'name': 'FA-18C Hornet (SOLDIER)'},
            '579': {'type': 'aircraft_dat', 'name': 'EA-18G (SOLDIER)'},
            '580': {'type': 'aircraft_dat', 'name': 'F-16C Fighting Falcon (SOLDIER)'},
            '581': {'type': 'aircraft_dat', 'name': 'F-16 XL (SOLDIER)'},
            '582': {'type': 'aircraft_dat', 'name': 'F-117A Nighthawk (SOLDIER)'},
            '583': {'type': 'aircraft_dat', 'name': 'FA-22A Raptor -MOBIUS- (SOLDIER)'},
            '584': {'type': 'aircraft_dat', 'name': 'F-35C (SOLDIER)'},
            '585': {'type': 'aircraft_dat', 'name': 'F-5E Tiger II (SOLDIER)'},
            '586': {'type': 'aircraft_dat', 'name': 'F-20A Tigershark (SOLDIER)'},
            '587': {'type': 'aircraft_dat', 'name': 'X-29A (SOLDIER)'},
            '588': {'type': 'aircraft_dat', 'name': 'F-14D Super Tomcat -RAZGRIZ- (SOLDIER)'},
            '589': {'type': 'aircraft_dat', 'name': 'YF-23A Black Widow II (SOLDIER)'},
            '590': {'type': 'aircraft_dat', 'name': 'EA-6B Prowler (SOLDIER)'},
            '591': {'type': 'aircraft_dat', 'name': 'A-10A Thunderbolt II (SOLDIER)'},
            '592': {'type': 'aircraft_dat', 'name': 'Mirage 2000D (SOLDIER)'},
            '593': {'type': 'aircraft_dat', 'name': 'Rafale M (SOLDIER)'},
            '594': {'type': 'aircraft_dat', 'name': 'Su-27 Flanker (SOLDIER)'},
            '595': {'type': 'aircraft_dat', 'name': 'Su-32 Super Flanker (SOLDIER)'},
            '596': {'type': 'aircraft_dat', 'name': 'Su-37 Terminator (SOLDIER)'},
            '597': {'type': 'aircraft_dat', 'name': 'Su-47 Berkut (SOLDIER)'},
            '598': {'type': 'aircraft_dat', 'name': 'MiG-21bis Fishbed (SOLDIER)'},
            '599': {'type': 'aircraft_dat', 'name': 'MiG-29A Fulcrum (SOLDIER)'},
            '600': {'type': 'aircraft_dat', 'name': 'MiG-31 Foxhound (SOLDIER)'},
            '601': {'type': 'aircraft_dat', 'name': 'F1 (SOLDIER)'},
            '602': {'type': 'aircraft_dat', 'name': 'F-2A (SOLDIER)'},
            '603': {'type': 'aircraft_dat', 'name': 'X-02 Wyvern (SOLDIER)'},
            '604': {'type': 'aircraft_dat', 'name': 'ADF-01 Falken (SOLDIER)'},
            '605': {'type': 'aircraft_dat', 'name': 'ADFX-01 Morgan (SOLDIER)'},
            '606': {'type': 'aircraft_dat', 'name': 'J35J Draken -ESPADA- (SPECIAL)'},
            '607': {'type': 'aircraft_dat', 'name': 'Gripen C -INDIGO- (SPECIAL)'},
            '608': {'type': 'aircraft_dat', 'name': 'Typhoon -ROT- (SPECIAL)'},
            '609': {'type': 'aircraft_dat', 'name': 'Tornado GR4 (SPECIAL)'},
            '610': {'type': 'aircraft_dat', 'name': 'F-4E II Phantom -SILBER- (SPECIAL)'},
            '611': {'type': 'aircraft_dat', 'name': 'F-15C Eagle (SPECIAL)'},
            '612': {'type': 'aircraft_dat', 'name': 'F-15 Strike Eagle (SPECIAL)'},
            '613': {'type': 'aircraft_dat', 'name': 'F-15 SMTD -SORCERER- (SPECIAL)'},
            '614': {'type': 'aircraft_dat', 'name': 'FA-18C Hornet -GRUN- (SPECIAL)'},
            '615': {'type': 'aircraft_dat', 'name': 'EA-18G (SPECIAL)'},
            '616': {'type': 'aircraft_dat', 'name': 'F-16C Fighting Falcon -SILBER- (SPECIAL)'},
            '617': {'type': 'aircraft_dat', 'name': 'F-16 XL -WIZARD- (SPECIAL)'},
            '618': {'type': 'aircraft_dat', 'name': 'F-117A Nighthawk (SPECIAL)'},
            '619': {'type': 'aircraft_dat', 'name': 'FA-22A Raptor (SPECIAL)'},
            '620': {'type': 'aircraft_dat', 'name': 'F-35C (SPECIAL)'},
            '621': {'type': 'aircraft_dat', 'name': 'F-5E Tiger II (SPECIAL)'},
            '622': {'type': 'aircraft_dat', 'name': 'F-20A Tigershark (SPECIAL)'},
            '623': {'type': 'aircraft_dat', 'name': 'X-29A (SPECIAL)'},
            '624': {'type': 'aircraft_dat', 'name': 'F-14D Super Tomcat -SCHNEE- (SPECIAL)'},
            '625': {'type': 'aircraft_dat', 'name': 'YF-23A Black Widow II -WIZARD- (SPECIAL)'},
            '626': {'type': 'aircraft_dat', 'name': 'EA-6B Prowler (SPECIAL)'},
            '627': {'type': 'aircraft_dat', 'name': 'A-10A Thunderbolt II (SPECIAL)'},
            '628': {'type': 'aircraft_dat', 'name': 'Mirage 2000D (SPECIAL)'},
            '629': {'type': 'aircraft_dat', 'name': 'Rafale M -ESPADA- (SPECIAL)'},
            '630': {'type': 'aircraft_dat', 'name': 'Su-27 Flanker (SPECIAL)'},
            '631': {'type': 'aircraft_dat', 'name': 'Su-32 Super Flanker (SPECIAL)'},
            '632': {'type': 'aircraft_dat', 'name': 'Su-37 Terminator -GELB- (SPECIAL)'},
            '633': {'type': 'aircraft_dat', 'name': 'Su-47 Berkut -GAULT- (SPECIAL)'},
            '634': {'type': 'aircraft_dat', 'name': 'MiG-21bis Fishbed -HUCKEBEIN- (SPECIAL)'},
            '635': {'type': 'aircraft_dat', 'name': 'MiG-29A Fulcrum (SPECIAL)'},
            '636': {'type': 'aircraft_dat', 'name': 'MiG-31 Foxhound -SCHWARZE- (SPECIAL)'},
            '637': {'type': 'aircraft_dat', 'name': 'F1 (SPECIAL)'},
            '638': {'type': 'aircraft_dat', 'name': 'F-2A (SPECIAL)'},
            '639': {'type': 'aircraft_dat', 'name': 'X-02 Wyvern (SPECIAL)'},
            '640': {'type': 'aircraft_dat', 'name': 'ADF-01 Falken (SPECIAL)'},
            '641': {'type': 'aircraft_dat', 'name': 'ADFX-01 Morgan -PIXY- (SPECIAL)'},
            '642': {'type': 'aircraft_dat', 'name': 'J35J Draken (KNIGHT)'},
            '643': {'type': 'aircraft_dat', 'name': 'Gripen C (KNIGHT)'},
            '644': {'type': 'aircraft_dat', 'name': 'Typhoon (KNIGHT)'},
            '645': {'type': 'aircraft_dat', 'name': 'Tornado GR4 (KNIGHT)'},
            '646': {'type': 'aircraft_dat', 'name': 'F-4E II Phantom (KNIGHT)'},
            '647': {'type': 'aircraft_dat', 'name': 'F-15C Eagle (KNIGHT)'},
            '648': {'type': 'aircraft_dat', 'name': 'F-15 Strike Eagle (KNIGHT)'},
            '649': {'type': 'aircraft_dat', 'name': 'F-15 SMTD (KNIGHT)'},
            '650': {'type': 'aircraft_dat', 'name': 'FA-18C Hornet (KNIGHT)'},
            '651': {'type': 'aircraft_dat', 'name': 'EA-18G (KNIGHT)'},
            '652': {'type': 'aircraft_dat', 'name': 'F-16C Fighting Falcon (KNIGHT)'},
            '653': {'type': 'aircraft_dat', 'name': 'F-16 XL (KNIGHT)'},
            '654': {'type': 'aircraft_dat', 'name': 'F-117A Nighthawk (KNIGHT)'},
            '655': {'type': 'aircraft_dat', 'name': 'FA-22A Raptor (KNIGHT)'},
            '656': {'type': 'aircraft_dat', 'name': 'F-35C (KNIGHT)'},
            '657': {'type': 'aircraft_dat', 'name': 'F-5E Tiger II (KNIGHT)'},
            '658': {'type': 'aircraft_dat', 'name': 'F-20A Tigershark (KNIGHT)'},
            '659': {'type': 'aircraft_dat', 'name': 'X-29A (KNIGHT)'},
            '660': {'type': 'aircraft_dat', 'name': 'F-14D Super Tomcat (KNIGHT)'},
            '661': {'type': 'aircraft_dat', 'name': 'YF-23A Black Widow II (KNIGHT)'},
            '662': {'type': 'aircraft_dat', 'name': 'EA-6B Prowler (KNIGHT)'},
            '663': {'type': 'aircraft_dat', 'name': 'A-10A Thunderbolt II (KNIGHT)'},
            '664': {'type': 'aircraft_dat', 'name': 'Mirage 2000D (KNIGHT)'},
            '665': {'type': 'aircraft_dat', 'name': 'Rafale M (KNIGHT)'},
            '666': {'type': 'aircraft_dat', 'name': 'Su-27 Flanker (KNIGHT)'},
            '667': {'type': 'aircraft_dat', 'name': 'Su-32 Super Flanker (KNIGHT)'},
            '668': {'type': 'aircraft_dat', 'name': 'Su-37 Terminator (KNIGHT)'},
            '669': {'type': 'aircraft_dat', 'name': 'Su-47 Berkut (KNIGHT)'},
            '670': {'type': 'aircraft_dat', 'name': 'MiG-21bis Fishbed (KNIGHT)'},
            '671': {'type': 'aircraft_dat', 'name': 'MiG-29A Fulcrum (KNIGHT)'},
            '672': {'type': 'aircraft_dat', 'name': 'MiG-31 Foxhound (KNIGHT)'},
            '673': {'type': 'aircraft_dat', 'name': 'F1 (KNIGHT)'},
            '674': {'type': 'aircraft_dat', 'name': 'F-2A (KNIGHT)'},
            '675': {'type': 'aircraft_dat', 'name': 'X-02 Wyvern (KNIGHT)'},
            '676': {'type': 'aircraft_dat', 'name': 'ADF-01 Falken (KNIGHT)'},
            '677': {'type': 'aircraft_dat', 'name': 'ADFX-01 Morgan (KNIGHT)'},
            #
            # Irregular/unused/special one-off aircraft skin slots (not part
            # of the systematic 5-tier grid above, but still aircraft-shaped
            # data) - unnamed slots in this range are omitted, same as
            # elsewhere.
            '678': {'type': 'aircraft_dat', 'name': 'Unused plane (F-16C cockpit assets)'},
            '679': {'type': 'aircraft_dat', 'name': 'Gripen C -INDIGO- (UNUSED)'},
            '680': {'type': 'aircraft_dat', 'name': 'Typhoon -ROT- (UNUSED)'},
            '681': {'type': 'aircraft_dat', 'name': 'J35J Draken -ESPADA- (UNUSED)'},
            '682': {'type': 'aircraft_dat', 'name': 'F-4E II Phantom -SILBER- (UNUSED)'},
            '683': {'type': 'aircraft_dat', 'name': 'F-15C Eagle (PIXY)'},
            '684': {'type': 'aircraft_dat', 'name': 'Unused plane (F-15E assets)'},
            '685': {'type': 'aircraft_dat', 'name': 'F-15 SMTD -SORCERER- (UNUSED)'},
            '686': {'type': 'aircraft_dat', 'name': 'FA-18C Hornet -GRUN- (SPECIAL)'},
            '688': {'type': 'aircraft_dat', 'name': 'F-16C Fighting Falcon (PJ)'},
            '689': {'type': 'aircraft_dat', 'name': 'F-16 XL -WIZARD- (UNUSED)'},
            '690': {'type': 'aircraft_dat', 'name': 'F-16C Fighting Falcon -SILBER- (UNUSED)'},
            '696': {'type': 'aircraft_dat', 'name': 'F-14D Super Tomcat -SCHNEE- (UNUSED)'},
            '701': {'type': 'aircraft_dat', 'name': 'Rafale M -ESPADA- (UNUSED)'},
            '704': {'type': 'aircraft_dat', 'name': 'Su-37 Terminator -GELB- (UNUSED)'},
            '705': {'type': 'aircraft_dat', 'name': 'Su-47 Berkut -GAULT- (UNUSED)'},
            '706': {'type': 'aircraft_dat', 'name': 'MiG-21bis Fishbed -HUCKEBEIN- (UNUSED)'},
            '708': {'type': 'aircraft_dat', 'name': 'MiG-31 Foxhound -SCHWARZE- (UNUSED)'},
            '713': {'type': 'aircraft_dat', 'name': 'ADFX-01 Morgan -PIXY- (UNUSED)'},
            '714': {'type': 'aircraft_dat', 'name': 'F-15C PIXY (WINGMAN)'},
            '715': {'type': 'aircraft_dat', 'name': 'F-16C PJ (WINGMAN)'},
            #
            # Hangar building/environment assets (not per-aircraft).
            '716': {'type': 'hangar_dat', 'name': 'Valais AFB'},
            '717': {'type': 'hangar_dat', 'name': 'Heierlark AFB'},
            '718': {'type': 'hangar_dat', 'name': 'Kirwin Island AFB'},
            '719': {'type': 'hangar_dat', 'name': 'Valais SP AFB'},
            #
            # Hangar-quality (higher-detail) aircraft models - same 5-tier
            # grid as the flyable aircraft above.
            '720': {'type': 'aircraft_hangar_dat', 'name': 'J35J Draken (STANDARD)'},
            '721': {'type': 'aircraft_hangar_dat', 'name': 'Gripen C (STANDARD)'},
            '722': {'type': 'aircraft_hangar_dat', 'name': 'Typhoon (STANDARD)'},
            '723': {'type': 'aircraft_hangar_dat', 'name': 'Tornado GR4 (STANDARD)'},
            '724': {'type': 'aircraft_hangar_dat', 'name': 'F-4E II Phantom (STANDARD)'},
            '725': {'type': 'aircraft_hangar_dat', 'name': 'F-15C Eagle CIPHER (STANDARD)'},
            '726': {'type': 'aircraft_hangar_dat', 'name': 'F-15 Strike Eagle (STANDARD)'},
            '727': {'type': 'aircraft_hangar_dat', 'name': 'F-15 SMTD (STANDARD)'},
            '728': {'type': 'aircraft_hangar_dat', 'name': 'FA-18C Hornet (STANDARD)'},
            '729': {'type': 'aircraft_hangar_dat', 'name': 'EA-18G (STANDARD)'},
            '730': {'type': 'aircraft_hangar_dat', 'name': 'F-16C Fighting Falcon (STANDARD)'},
            '731': {'type': 'aircraft_hangar_dat', 'name': 'F-16 XL (STANDARD)'},
            '732': {'type': 'aircraft_hangar_dat', 'name': 'F-117A Nighthawk (STANDARD)'},
            '733': {'type': 'aircraft_hangar_dat', 'name': 'FA-22A Raptor (STANDARD)'},
            '734': {'type': 'aircraft_hangar_dat', 'name': 'F-35C (STANDARD)'},
            '735': {'type': 'aircraft_hangar_dat', 'name': 'F-5E Tiger II (STANDARD)'},
            '736': {'type': 'aircraft_hangar_dat', 'name': 'F-20A Tigershark (STANDARD)'},
            '737': {'type': 'aircraft_hangar_dat', 'name': 'X-29A (STANDARD)'},
            '738': {'type': 'aircraft_hangar_dat', 'name': 'F-14D Super Tomcat (STANDARD)'},
            '739': {'type': 'aircraft_hangar_dat', 'name': 'YF-23A Black Widow II (STANDARD)'},
            '740': {'type': 'aircraft_hangar_dat', 'name': 'EA-6B Prowler (STANDARD)'},
            '741': {'type': 'aircraft_hangar_dat', 'name': 'A-10A Thunderbolt II (STANDARD)'},
            '742': {'type': 'aircraft_hangar_dat', 'name': 'Mirage 2000D (STANDARD)'},
            '743': {'type': 'aircraft_hangar_dat', 'name': 'Rafale M (STANDARD)'},
            '744': {'type': 'aircraft_hangar_dat', 'name': 'Su-27 Flanker (STANDARD)'},
            '745': {'type': 'aircraft_hangar_dat', 'name': 'Su-32 Super Flanker (STANDARD)'},
            '746': {'type': 'aircraft_hangar_dat', 'name': 'Su-37 Terminator (STANDARD)'},
            '747': {'type': 'aircraft_hangar_dat', 'name': 'Su-47 Berkut (STANDARD)'},
            '748': {'type': 'aircraft_hangar_dat', 'name': 'MiG-21bis Fishbed (STANDARD)'},
            '749': {'type': 'aircraft_hangar_dat', 'name': 'MiG-29A Fulcrum (STANDARD)'},
            '750': {'type': 'aircraft_hangar_dat', 'name': 'MiG-31 Foxhound (STANDARD)'},
            '751': {'type': 'aircraft_hangar_dat', 'name': 'F1 (STANDARD)'},
            '752': {'type': 'aircraft_hangar_dat', 'name': 'F-2A (STANDARD)'},
            '753': {'type': 'aircraft_hangar_dat', 'name': 'X-02 Wyvern (STANDARD)'},
            '754': {'type': 'aircraft_hangar_dat', 'name': 'ADF-01 Falken (STANDARD)'},
            '755': {'type': 'aircraft_hangar_dat', 'name': 'ADFX-01 Morgan (STANDARD)'},
            '756': {'type': 'aircraft_hangar_dat', 'name': 'J35J Draken (MERCENARY)'},
            '757': {'type': 'aircraft_hangar_dat', 'name': 'Gripen C (MERCENARY)'},
            '758': {'type': 'aircraft_hangar_dat', 'name': 'Typhoon (MERCENARY)'},
            '759': {'type': 'aircraft_hangar_dat', 'name': 'Tornado GR4 (MERCENARY)'},
            '760': {'type': 'aircraft_hangar_dat', 'name': 'F-4E II Phantom (MERCENARY)'},
            '761': {'type': 'aircraft_hangar_dat', 'name': 'F-15C Eagle (MERCENARY)'},
            '762': {'type': 'aircraft_hangar_dat', 'name': 'F-15 Strike Eagle (MERCENARY)'},
            '763': {'type': 'aircraft_hangar_dat', 'name': 'F-15 SMTD (MERCENARY)'},
            '764': {'type': 'aircraft_hangar_dat', 'name': 'FA-18C Hornet (MERCENARY)'},
            '765': {'type': 'aircraft_hangar_dat', 'name': 'EA-18G (MERCENARY)'},
            '766': {'type': 'aircraft_hangar_dat', 'name': 'F-16C Fighting Falcon (MERCENARY)'},
            '767': {'type': 'aircraft_hangar_dat', 'name': 'F-16 XL (MERCENARY)'},
            '768': {'type': 'aircraft_hangar_dat', 'name': 'F-117A Nighthawk (MERCENARY)'},
            '769': {'type': 'aircraft_hangar_dat', 'name': 'FA-22A Raptor (MERCENARY)'},
            '770': {'type': 'aircraft_hangar_dat', 'name': 'F-35C (MERCENARY)'},
            '771': {'type': 'aircraft_hangar_dat', 'name': 'F-5E Tiger II (MERCENARY)'},
            '772': {'type': 'aircraft_hangar_dat', 'name': 'F-20A Tigershark (MERCENARY)'},
            '773': {'type': 'aircraft_hangar_dat', 'name': 'X-29A (MERCENARY)'},
            '774': {'type': 'aircraft_hangar_dat', 'name': 'F-14D Super Tomcat (MERCENARY)'},
            '775': {'type': 'aircraft_hangar_dat', 'name': 'YF-23A Black Widow II (MERCENARY)'},
            '776': {'type': 'aircraft_hangar_dat', 'name': 'EA-6B Prowler (MERCENARY)'},
            '777': {'type': 'aircraft_hangar_dat', 'name': 'A-10A Thunderbolt II (MERCENARY)'},
            '778': {'type': 'aircraft_hangar_dat', 'name': 'Mirage 2000D (MERCENARY)'},
            '779': {'type': 'aircraft_hangar_dat', 'name': 'Rafale M (MERCENARY)'},
            '780': {'type': 'aircraft_hangar_dat', 'name': 'Su-27 Flanker (MERCENARY)'},
            '781': {'type': 'aircraft_hangar_dat', 'name': 'Su-32 Super Flanker (MERCENARY)'},
            '782': {'type': 'aircraft_hangar_dat', 'name': 'Su-37 Terminator YELLOW (MERCENARY)'},
            '783': {'type': 'aircraft_hangar_dat', 'name': 'Su-47 Berkut (MERCENARY)'},
            '784': {'type': 'aircraft_hangar_dat', 'name': 'MiG-21bis Fishbed (MERCENARY)'},
            '785': {'type': 'aircraft_hangar_dat', 'name': 'MiG-29A Fulcrum (MERCENARY)'},
            '786': {'type': 'aircraft_hangar_dat', 'name': 'MiG-31 Foxhound (MERCENARY)'},
            '787': {'type': 'aircraft_hangar_dat', 'name': 'F1 (MERCENARY)'},
            '788': {'type': 'aircraft_hangar_dat', 'name': 'F-2A (MERCENARY)'},
            '789': {'type': 'aircraft_hangar_dat', 'name': 'X-02 Wyvern (MERCENARY)'},
            '790': {'type': 'aircraft_hangar_dat', 'name': 'ADF-01 Falken (MERCENARY)'},
            '791': {'type': 'aircraft_hangar_dat', 'name': 'ADFX-01 Morgan (MERCENARY)'},
            '792': {'type': 'aircraft_hangar_dat', 'name': 'J35J Draken (SOLDIER)'},
            '793': {'type': 'aircraft_hangar_dat', 'name': 'Gripen C (SOLDIER)'},
            '794': {'type': 'aircraft_hangar_dat', 'name': 'Typhoon (SOLDIER)'},
            '795': {'type': 'aircraft_hangar_dat', 'name': 'Tornado GR4 (SOLDIER)'},
            '796': {'type': 'aircraft_hangar_dat', 'name': 'F-4E II Phantom (SOLDIER)'},
            '797': {'type': 'aircraft_hangar_dat', 'name': 'F-15C Eagle (SOLDIER)'},
            '798': {'type': 'aircraft_hangar_dat', 'name': 'F-15 Strike Eagle (SOLDIER)'},
            '799': {'type': 'aircraft_hangar_dat', 'name': 'F-15 SMTD (SOLDIER)'},
            '800': {'type': 'aircraft_hangar_dat', 'name': 'FA-18C Hornet (SOLDIER)'},
            '801': {'type': 'aircraft_hangar_dat', 'name': 'EA-18G (SOLDIER)'},
            '802': {'type': 'aircraft_hangar_dat', 'name': 'F-16C Fighting Falcon (SOLDIER)'},
            '803': {'type': 'aircraft_hangar_dat', 'name': 'F-16 XL (SOLDIER)'},
            '804': {'type': 'aircraft_hangar_dat', 'name': 'F-117A Nighthawk (SOLDIER)'},
            '805': {'type': 'aircraft_hangar_dat', 'name': 'FA-22A Raptor MOBIUS (SOLDIER)'},
            '806': {'type': 'aircraft_hangar_dat', 'name': 'F-35C (SOLDIER)'},
            '807': {'type': 'aircraft_hangar_dat', 'name': 'F-5E Tiger II (SOLDIER)'},
            '808': {'type': 'aircraft_hangar_dat', 'name': 'F-20A Tigershark (SOLDIER)'},
            '809': {'type': 'aircraft_hangar_dat', 'name': 'X-29A (SOLDIER)'},
            '810': {'type': 'aircraft_hangar_dat', 'name': 'F-14D Super Tomcat RAZGRIZ (SOLDIER)'},
            '811': {'type': 'aircraft_hangar_dat', 'name': 'YF-23A Black Widow II (SOLDIER)'},
            '812': {'type': 'aircraft_hangar_dat', 'name': 'EA-6B Prowler (SOLDIER)'},
            '813': {'type': 'aircraft_hangar_dat', 'name': 'A-10A Thunderbolt II (SOLDIER)'},
            '814': {'type': 'aircraft_hangar_dat', 'name': 'Mirage 2000D (SOLDIER)'},
            '815': {'type': 'aircraft_hangar_dat', 'name': 'Rafale M (SOLDIER)'},
            '816': {'type': 'aircraft_hangar_dat', 'name': 'Su-27 Flanker (SOLDIER)'},
            '817': {'type': 'aircraft_hangar_dat', 'name': 'Su-32 Super Flanker (SOLDIER)'},
            '818': {'type': 'aircraft_hangar_dat', 'name': 'Su-37 Terminator (SOLDIER)'},
            '819': {'type': 'aircraft_hangar_dat', 'name': 'Su-47 Berkut (SOLDIER)'},
            '820': {'type': 'aircraft_hangar_dat', 'name': 'MiG-21bis Fishbed (SOLDIER)'},
            '821': {'type': 'aircraft_hangar_dat', 'name': 'MiG-29A Fulcrum (SOLDIER)'},
            '822': {'type': 'aircraft_hangar_dat', 'name': 'MiG-31 Foxhound (SOLDIER)'},
            '823': {'type': 'aircraft_hangar_dat', 'name': 'F1 (SOLDIER)'},
            '824': {'type': 'aircraft_hangar_dat', 'name': 'F-2A (SOLDIER)'},
            '825': {'type': 'aircraft_hangar_dat', 'name': 'X-02 Wyvern (SOLDIER)'},
            '826': {'type': 'aircraft_hangar_dat', 'name': 'ADF-01 Falken (SOLDIER)'},
            '827': {'type': 'aircraft_hangar_dat', 'name': 'ADFX-01 Morgan (SOLDIER)'},
            '828': {'type': 'aircraft_hangar_dat', 'name': 'J35J Draken -ESPADA- (SPECIAL)'},
            '829': {'type': 'aircraft_hangar_dat', 'name': 'Gripen C -INDIGO- (SPECIAL)'},
            '830': {'type': 'aircraft_hangar_dat', 'name': 'Typhoon -ROT- (SPECIAL)'},
            '832': {'type': 'aircraft_hangar_dat', 'name': 'F-4E II Phantom -SILBER- (SPECIAL)'},
            '835': {'type': 'aircraft_hangar_dat', 'name': 'F-15 SMTD -SORCERER- (SPECIAL)'},
            '836': {'type': 'aircraft_hangar_dat', 'name': 'FA-18C Hornet -GRUN- (SPECIAL)'},
            '838': {'type': 'aircraft_hangar_dat', 'name': 'F-16C Fighting Falcon -SILBER- (SPECIAL)'},
            '839': {'type': 'aircraft_hangar_dat', 'name': 'F-16 XL -WIZARD- (SPECIAL)'},
            '846': {'type': 'aircraft_hangar_dat', 'name': 'F-14D Super Tomcat -SCHNEE- (SPECIAL)'},
            '847': {'type': 'aircraft_hangar_dat', 'name': 'YF-23A Black Widow II -WIZARD- (SPECIAL)'},
            '851': {'type': 'aircraft_hangar_dat', 'name': 'Rafale M -ESPADA- (SPECIAL)'},
            '854': {'type': 'aircraft_hangar_dat', 'name': 'Su-37 Terminator GELB (SPECIAL)'},
            '855': {'type': 'aircraft_hangar_dat', 'name': 'Su-47 Berkut -GAULT- (SPECIAL)'},
            '858': {'type': 'aircraft_hangar_dat', 'name': 'MiG-31 Foxhound -SCHWARZE- (SPECIAL)'},
            '863': {'type': 'aircraft_hangar_dat', 'name': 'ADFX-01 Morgan PIXY (SPECIAL)'},
            '867': {'type': 'aircraft_hangar_dat', 'name': 'Tornado GR4 (SPECIAL)'},
            '869': {'type': 'aircraft_hangar_dat', 'name': 'F-15C Eagle (SPECIAL)'},
            '870': {'type': 'aircraft_hangar_dat', 'name': 'F-15 Strike Eagle (SPECIAL)'},
            '873': {'type': 'aircraft_hangar_dat', 'name': 'EA-18G (SPECIAL)'},
            '876': {'type': 'aircraft_hangar_dat', 'name': 'F-117A Nighthawk (SPECIAL)'},
            '877': {'type': 'aircraft_hangar_dat', 'name': 'FA-22A Raptor (SPECIAL)'},
            '878': {'type': 'aircraft_hangar_dat', 'name': 'F-35C (SPECIAL)'},
            '879': {'type': 'aircraft_hangar_dat', 'name': 'F-5E Tiger II (SPECIAL)'},
            '880': {'type': 'aircraft_hangar_dat', 'name': 'F-20A Tigershark (SPECIAL)'},
            '881': {'type': 'aircraft_hangar_dat', 'name': 'X-29A (SPECIAL)'},
            '884': {'type': 'aircraft_hangar_dat', 'name': 'EA-6B Prowler (SPECIAL)'},
            '885': {'type': 'aircraft_hangar_dat', 'name': 'A-10A Thunderbolt II (SPECIAL)'},
            '886': {'type': 'aircraft_hangar_dat', 'name': 'Mirage 2000D (SPECIAL)'},
            '888': {'type': 'aircraft_hangar_dat', 'name': 'Su-27 Flanker (SPECIAL)'},
            '889': {'type': 'aircraft_hangar_dat', 'name': 'Su-32 Super Flanker (SPECIAL)'},
            '892': {'type': 'aircraft_hangar_dat', 'name': 'MiG-21bis Fishbed HUCKEBEIN (SPECIAL)'},
            '893': {'type': 'aircraft_hangar_dat', 'name': 'MiG-29A Fulcrum (SPECIAL)'},
            '895': {'type': 'aircraft_hangar_dat', 'name': 'F1 (SPECIAL)'},
            '896': {'type': 'aircraft_hangar_dat', 'name': 'F-2A (SPECIAL)'},
            '897': {'type': 'aircraft_hangar_dat', 'name': 'X-02 Wyvern (SPECIAL)'},
            '898': {'type': 'aircraft_hangar_dat', 'name': 'ADF-01 Falken (SPECIAL)'},
            '900': {'type': 'aircraft_hangar_dat', 'name': 'J35J Draken (KNIGHT)'},
            '901': {'type': 'aircraft_hangar_dat', 'name': 'Gripen C (KNIGHT)'},
            '902': {'type': 'aircraft_hangar_dat', 'name': 'Typhoon (KNIGHT)'},
            '903': {'type': 'aircraft_hangar_dat', 'name': 'Tornado GR4 (KNIGHT)'},
            '904': {'type': 'aircraft_hangar_dat', 'name': 'F-4E II Phantom (KNIGHT)'},
            '905': {'type': 'aircraft_hangar_dat', 'name': 'F-15C Eagle (KNIGHT)'},
            '906': {'type': 'aircraft_hangar_dat', 'name': 'F-15 Strike Eagle (KNIGHT)'},
            '907': {'type': 'aircraft_hangar_dat', 'name': 'F-15 SMTD (KNIGHT)'},
            '908': {'type': 'aircraft_hangar_dat', 'name': 'FA-18C Hornet (KNIGHT)'},
            '909': {'type': 'aircraft_hangar_dat', 'name': 'EA-18G (KNIGHT)'},
            '910': {'type': 'aircraft_hangar_dat', 'name': 'F-16C Fighting Falcon (KNIGHT)'},
            '911': {'type': 'aircraft_hangar_dat', 'name': 'F-16 XL (KNIGHT)'},
            '912': {'type': 'aircraft_hangar_dat', 'name': 'F-117A Nighthawk (KNIGHT)'},
            '913': {'type': 'aircraft_hangar_dat', 'name': 'FA-22A Raptor (KNIGHT)'},
            '914': {'type': 'aircraft_hangar_dat', 'name': 'F-35C (KNIGHT)'},
            '915': {'type': 'aircraft_hangar_dat', 'name': 'F-5E Tiger II (KNIGHT)'},
            '916': {'type': 'aircraft_hangar_dat', 'name': 'F-20A Tigershark (KNIGHT)'},
            '917': {'type': 'aircraft_hangar_dat', 'name': 'X-29A (KNIGHT)'},
            '918': {'type': 'aircraft_hangar_dat', 'name': 'F-14D Super Tomcat (KNIGHT)'},
            '919': {'type': 'aircraft_hangar_dat', 'name': 'YF-23A Black Widow II (KNIGHT)'},
            '920': {'type': 'aircraft_hangar_dat', 'name': 'EA-6B Prowler (KNIGHT)'},
            '921': {'type': 'aircraft_hangar_dat', 'name': 'A-10A Thunderbolt II (KNIGHT)'},
            '922': {'type': 'aircraft_hangar_dat', 'name': 'Mirage 2000D (KNIGHT)'},
            '923': {'type': 'aircraft_hangar_dat', 'name': 'Rafale M (KNIGHT)'},
            '924': {'type': 'aircraft_hangar_dat', 'name': 'Su-27 Flanker (KNIGHT)'},
            '925': {'type': 'aircraft_hangar_dat', 'name': 'Su-32 Super Flanker (KNIGHT)'},
            '926': {'type': 'aircraft_hangar_dat', 'name': 'Su-37 Terminator (KNIGHT)'},
            '927': {'type': 'aircraft_hangar_dat', 'name': 'Su-47 Berkut (KNIGHT)'},
            '928': {'type': 'aircraft_hangar_dat', 'name': 'MiG-21bis Fishbed (KNIGHT)'},
            '929': {'type': 'aircraft_hangar_dat', 'name': 'MiG-29A Fulcrum (KNIGHT)'},
            '930': {'type': 'aircraft_hangar_dat', 'name': 'MiG-31 Foxhound (KNIGHT)'},
            '931': {'type': 'aircraft_hangar_dat', 'name': 'F1 (KNIGHT)'},
            '932': {'type': 'aircraft_hangar_dat', 'name': 'F-2A (KNIGHT)'},
            '933': {'type': 'aircraft_hangar_dat', 'name': 'X-02 Wyvern (KNIGHT)'},
            '934': {'type': 'aircraft_hangar_dat', 'name': 'ADF-01 Falken (KNIGHT)'},
            '935': {'type': 'aircraft_hangar_dat', 'name': 'ADFX-01 Morgan (KNIGHT)'},
            '941': {'type': 'aircraft_hangar_dat', 'name': 'F-15C Eagle (PIXY)'},
            '946': {'type': 'aircraft_hangar_dat', 'name': 'F-16C Fighting Falcon (PJ)'},
            #
            # Named but structurally unverified - carried over for
            # documentation without a dedicated parsed type (see TASKS.md).
            '1160': {'type': '', 'name': 'MPBM hangar assets'},
            '1170': {'type': '', 'name': 'TLS unit hangar assets (ADFX-01)'},
            '1171': {'type': '', 'name': 'TLS unit hangar assets (ADF-01)'},
            '1448': {'type': '', 'name': 'Hangar aircraft prices and satellite-plot chart parameters'},
            #
            # Per-mission briefing digitized terrain assets.
            '1430': {'type': 'briefing_terrain_dat', 'name': 'M01 briefing digitized terrain assets'},
            '1431': {'type': 'briefing_terrain_dat', 'name': 'M02 briefing digitized terrain assets'},
            '1432': {'type': 'briefing_terrain_dat', 'name': 'M03 briefing digitized terrain assets'},
            '1433': {'type': 'briefing_terrain_dat', 'name': 'M04 briefing digitized terrain assets'},
            '1434': {'type': 'briefing_terrain_dat', 'name': 'M05 briefing digitized terrain assets'},
            '1435': {'type': 'briefing_terrain_dat', 'name': 'M06 briefing digitized terrain assets'},
            '1436': {'type': 'briefing_terrain_dat', 'name': 'M07 briefing digitized terrain assets'},
            '1437': {'type': 'briefing_terrain_dat', 'name': 'M08 briefing digitized terrain assets'},
            '1438': {'type': 'briefing_terrain_dat', 'name': 'M09 briefing digitized terrain assets'},
            '1439': {'type': 'briefing_terrain_dat', 'name': 'M10 briefing digitized terrain assets'},
            '1440': {'type': 'briefing_terrain_dat', 'name': 'M11 briefing digitized terrain assets'},
            '1441': {'type': 'briefing_terrain_dat', 'name': 'M12 briefing digitized terrain assets'},
            '1442': {'type': 'briefing_terrain_dat', 'name': 'M13 briefing digitized terrain assets'},
            '1443': {'type': 'briefing_terrain_dat', 'name': 'M14 briefing digitized terrain assets'},
            '1444': {'type': 'briefing_terrain_dat', 'name': 'M15 briefing digitized terrain assets'},
            '1445': {'type': 'briefing_terrain_dat', 'name': 'M16 briefing digitized terrain assets'},
            '1446': {'type': 'briefing_terrain_dat', 'name': 'M17 briefing digitized terrain assets'},
            '1447': {'type': 'briefing_terrain_dat', 'name': 'M18 briefing digitized terrain assets'},
            #
            '1450': {'type': 'dat', 'name': 'Unnamed dat (assumed)'},
            #
            # Per-mission title card textures.
            '1451': {'type': 'title_card_dat', 'name': 'M01 title card texture'},
            '1452': {'type': 'title_card_dat', 'name': 'M02 title card texture'},
            '1453': {'type': 'title_card_dat', 'name': 'M03 title card texture'},
            '1454': {'type': 'title_card_dat', 'name': 'M04 title card texture'},
            '1455': {'type': 'title_card_dat', 'name': 'M05 title card texture'},
            '1456': {'type': 'title_card_dat', 'name': 'M06 title card texture'},
            '1457': {'type': 'title_card_dat', 'name': 'M07 title card texture'},
            '1458': {'type': 'title_card_dat', 'name': 'M08 title card texture'},
            '1459': {'type': 'title_card_dat', 'name': 'M09 title card texture'},
            '1460': {'type': 'title_card_dat', 'name': 'M10 title card texture'},
            '1461': {'type': 'title_card_dat', 'name': 'M11 title card texture'},
            '1462': {'type': 'title_card_dat', 'name': 'M12 title card texture'},
            '1463': {'type': 'title_card_dat', 'name': 'M13 title card texture'},
            '1464': {'type': 'title_card_dat', 'name': 'M14 title card texture'},
            '1465': {'type': 'title_card_dat', 'name': 'M15 title card texture'},
            '1466': {'type': 'title_card_dat', 'name': 'M16 title card texture'},
            '1467': {'type': 'title_card_dat', 'name': 'M17 title card texture'},
            '1468': {'type': 'title_card_dat', 'name': 'M18 title card texture'},
            '1469': {'type': 'title_card_dat', 'name': 'MSP title card texture'},
        }

        # Slot-by-slot contents of a stage .dat, per death_the_d0g's table.
        # Not yet applied anywhere (see TASKS/notes) - will later be hooked up
        # to type the children of 'stage_dat' (and, once confirmed, 'mission_dat')
        # containers, the same way ACZ_DAT_ASSET_LIST types DATA.PAC's own children.
        # TOC entries with a null (0x00000000) offset are skipped by the game at
        # load time - usually files holding only empty/unused parameters.
        self.ACZ_STAGE_DAT_ASSET_LIST = {
            '0': {'type': '', 'name': 'Terrain mesh tile placement map'},
            '1': {'type': '', 'name': 'Mesh tile data placement data'},
            '2': {'type': '', 'name': 'Unknown - affects tile texture'},
            '3': {'type': '', 'name': 'Unknown - affects tile texture'},
            '4': {'type': '', 'name': 'Terrain mesh vertex color data/Texture tile transparency'},
            '5': {'type': '', 'name': '1024x1024 texture tile placement map'},
            '6': {'type': '', 'name': '64x64 texture tile placement data'},
            '7': {'type': '', 'name': 'Terrain texture tile data'},
            '8': {'type': '', 'name': 'Terrain texture palette data'},
            '9': {'type': 'gim', 'name': 'Unknown texture file'},
            '10': {'type': 'gim', 'name': 'Main light source environment map texture'},
            '11': {'type': '', 'name': 'Skybox parameters and vertex color configuration'},
            '12': {'type': 'gim', 'name': 'Unknown texture file'},
            '13': {'type': '', 'name': 'Unknown data file - related to stage props (buildings, etc.)'},
            '14': {'type': '', 'name': 'Unknown data file, related to stage props (buildings, etc.)'},
            '15': {'type': '', 'name': 'Stage props ID and their coordinates data'},
            '16': {'type': '', 'name': 'Stage props 3D model data'},
            '17': {'type': '', 'name': 'Stage props texture data'},
            '18': {'type': '', 'name': "Stage's graphic configuration file"},
            '19': {'type': 'ambient_textures_dat', 'name': 'Skybox/weather texture files (shadow cloud map/moon/clouds/star/lens flare textures)'},
            '20': {'type': 'efd', 'name': 'Stage particle effect configuration file'},
            '21': {'type': 'gim', 'name': 'Particle effect texture sheet 1'},
            '22': {'type': 'gim', 'name': 'Particle effect texture sheet 2'},
            '23': {'type': 'gim', 'name': 'Unknown texture'},
            '24': {'type': 'gim', 'name': 'Radar map texture'},
            '25': {'type': '', 'name': 'Foliage tile placement map ?'},
            '26': {'type': '', 'name': 'Foliage tile data placement map ?'},
            '27': {'type': '', 'name': 'Related to foliage data'},
            '28': {'type': 'acm', 'name': 'Tree model file 1'},
            '29': {'type': 'acm', 'name': 'Tree model file 2'},
            '30': {'type': 'acm', 'name': 'Tree model file 3'},
            '31': {'type': 'gim', 'name': 'Tree texture file 1'},
            '32': {'type': 'gim', 'name': 'Tree texture file 2'},
            '33': {'type': 'gim', 'name': 'Tree texture file 3'},
            '34': {'type': '', 'name': 'Unknown data file'},
            '35': {'type': '', 'name': 'Unknown data file'},
            '36': {'type': '', 'name': 'Padding 0x10'},
            '37': {'type': '', 'name': "Stage's graphic configuration file"},
            '38': {'type': 'stage_dat', 'name': 'Null or landing stage data'},
        }

        # Slot-by-slot contents of a stage's ambient textures .dat (slot 19
        # of ACZ_STAGE_DAT_ASSET_LIST) - 12 GIM textures, purpose of each
        # individual slot not yet identified, so they're named positionally
        # (00-11) rather than guessed at.
        self.ACZ_AMBIENT_TEXTURES_ASSET_LIST = {
            '0': {'type': 'gim', 'name': '00'},
            '1': {'type': 'gim', 'name': '01'},
            '2': {'type': 'gim', 'name': '02'},
            '3': {'type': 'gim', 'name': '03'},
            '4': {'type': 'gim', 'name': '04'},
            '5': {'type': 'gim', 'name': '05'},
            '6': {'type': 'gim', 'name': '06'},
            '7': {'type': 'gim', 'name': '07'},
            '8': {'type': 'gim', 'name': '08'},
            '9': {'type': 'gim', 'name': '09'},
            '10': {'type': 'gim', 'name': '10'},
            '11': {'type': 'gim', 'name': '11'},
        }

        # Per-class asset tables for this game (see Project.asset_tables /
        # Container._resolve_asset_table). Any DatStage/DatAmbientTextures -
        # top-level or nested arbitrarily deep inside another one - resolves
        # its own table from this automatically at construction time; no
        # manual propagation needed.
        self.asset_tables = {
            DataPacAsset: self.ACZ_DAT_ASSET_LIST,
            DatStage: self.ACZ_STAGE_DAT_ASSET_LIST,
            DatAmbientTextures: self.ACZ_AMBIENT_TEXTURES_ASSET_LIST,
        }

        # Asset creation:
        self.DATA_PAC = DataPacAsset(name='DATA.PAC', size=os.stat(pac_path).st_size, offset = 0, data_ref=self._DATA_PAC_REF, index=0, father=self, asset_list=self.ACZ_DAT_ASSET_LIST)

        if False:
            def auto_apply_type(asset:Asset):
                ''' Autodetects an untyped asset's type and replaces it with the correct type.
                This is for assets that were not typed using a lookup table.
                asset: Asset to be replaced'''
                data = asset.get_raw_data()
                father = asset.father
                data_ref = asset.data_ref
                prefix = data[:3]
                key = asset.index_father

                #print(f'input index: {key} - Asset index: {asset.index_father}')
                #print(prefix)

                if prefix == b'GIM':
                    print('is GIM!')
                    new_asset = GIM(name=f'{key}.GIM', size=asset.size, offset=asset.offset_father, data_ref=data_ref, index=int(key), father=father)
                    father.generate_child(index=int(key), obj=new_asset)
                elif prefix == b'P3D':
                    print('is P3D!')
                    new_asset = P3D(name=f'{key}.P3D', size=asset.size, offset=asset.offset_father, data_ref=data_ref, index=int(key), father=father)
                    father.generate_child(index=int(key), obj=new_asset)

            # Check for file types inside .dats
            print('Analysing typed .dats')
            for dat_key, dat in self.DATA_PAC.children.items():
                if type(dat) is Asset: # Check if loose .dats have a file type.
                    auto_apply_type(asset=dat)
                #if type(dat) is DatMission:
                if isinstance(dat, Container): # Check for untyped files inside the .dats
                    for subdat_key, subdat in dat.children.items():
                        if type(subdat) is Asset:
                            auto_apply_type(asset=subdat)
                        

        pass
        






class DataReference():
    ''' This class hold the actual data.
    It is the representation of a file's raw data. '''
    # TODO: Consider passing the file's path instead of copying raw data.
    # It will save memory, make the process less verbose and mayber help with other optimizations.
    def __init__(self, name:str, raw_data:bytes):
        self._raw_data:bytes = raw_data
        self.size = len(raw_data)
        self._cursor:int = 0
        
    def read(self, size: int | None = None) -> bytes:
        if self._cursor >= self.size:
            return b''

        if size is None or size < 0:
            start = self._cursor
            self._cursor = self.size
            return self._raw_data[start:self.size]

        if size == 0:
            return b''

        start = self._cursor
        end = min(self._cursor + size, self.size)
        self._cursor = end
        return self._raw_data[start:end]

        
    def tell(self) -> int:
        return self._cursor

    def seek(self, pos: int, whence: int = 0) -> int:
        if whence == 0:      # absolute
            new_pos = pos
        elif whence == 1:    # relative
            new_pos = self._cursor + pos
        elif whence == 2:    # from end
            new_pos = self.size + pos
        else:
            raise ValueError("invalid whence")

        if new_pos < 0:
            raise ValueError("negative seek position")

        self._cursor = new_pos
        return self._cursor

    def get_remaining_length(self):
        # TODO: Apparently unused. cerify that.
        return max(0, self.size - self._cursor)

    def get_data(self, offset: int, length: int) -> bytes:
        # TODO: make length optional. When not used, returns remaining data.
        # TODO: Clamp 'end' value to remaining size. Consider using self.get_remaining_length
        if length <= 0:
            return b''

        if offset < 0:
            return b''

        if offset >= self.size:
            return b''

        end = offset + length
        return self._raw_data[offset:end]


class DataRefTbl(DataReference):
    def __init__(self, name:str, raw_data:bytes):
        super().__init__(name=name, raw_data=raw_data)
    
    def get_tbl_offset_table(self) -> list:
        # Returns the offset table and sizes from a .TBL file
        offset_list = []
        size_list = []

        #with open(tbl_path, 'rb') as self:
        self.seek(0)
        tbl_nof = int.from_bytes(self.read(4), byteorder="little")
        self.seek(8)
        for _ in range(tbl_nof):
            offset_list.append(int.from_bytes(self.read(4), byteorder="little"))
            size_list.append(int.from_bytes(self.read(4), byteorder="little"))

        return offset_list


class DataRefPac(DataReference):
    def __init__(self, name:str, raw_data:bytes, tbl_ref:DataRefTbl):
        super().__init__(name=name, raw_data=raw_data)
        self.tbl_ref = tbl_ref

    def get_offset_table(self):
        return self.tbl_ref.get_tbl_offset_table()



class Asset():
    def __init__(self, name:str, size:int, offset:int,
                 #ref_offset:int,
                 data_ref:DataReference, index:int, father):
        self.name = name
        self.size = size
        self.father:Asset = father
        self.offset_father = offset # Offset from its father container.
        self.index_father = index # Offset from its father container.
        self.data_ref = data_ref

    @property
    def offset_ref(self) -> int:
        '''Absolute offset from the root data reference. Computed live from the
        current offset_father/father chain (rather than cached at __init__ time)
        so it stays correct if offset_father is patched later, e.g. by
        Container.generate_child().'''
        if isinstance(self.father, Asset):
            return self.offset_father + self.father.offset_ref
        return self.offset_father

    @property
    def root_project(self):
        '''Walks up the father chain to the Project this asset ultimately
        belongs to (the first ancestor that isn't itself an Asset) - the
        same walking pattern as offset_ref, used to look up which
        game/project's data (like a per-class asset table) applies here.'''
        node = self.father
        while isinstance(node, Asset):
            node = node.father
        return node

    def get_raw_data(self) -> bytes:
        '''Returns this asset's own raw bytes, read from its data reference.'''
        return self.data_ref.get_data(self.offset_ref, self.size)

    def __repr__(self):
        return f'ASSET | ({self.index_father})_{self.name} - size={self.size} - offset={self.offset_father}'


class Container(Asset): # Abstract
    '''A simple container that has generic children based on a offset table
    and a hook for asset tables for future classes'''
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father, asset_list:dict=None):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
        self.offset_table = []
        self.sizes_list:list = []
        self.children = dict()
        # asset_list is an explicit override, for the rare exception that needs
        # one; the normal case is auto-resolving the right table for this
        # class from the active project, so every container (top-level or
        # nested arbitrarily deep) gets typed correctly with no manual wiring.
        self.asset_table:dict = asset_list if asset_list is not None else self._resolve_asset_table()

    def _resolve_asset_table(self) -> dict | None:
        project = self.root_project
        if project is None:
            return None
        return project.get_asset_table(type(self))

    def set_offset_table(self, offset_table:list):
        self.offset_table = offset_table[:]

    def init_offset_table(self):
        ref_table = self.offset_table[:]
        ref_table.append(self.size)

        for i, offset in enumerate(ref_table):
            if i == len(ref_table)-1:
                break
            aux_size = ref_table[i+1] - ref_table[i]
            self.sizes_list.append(aux_size)

    def generate_generic_children(self):
        '''Generates all children of the container'''
        for i, offset in enumerate(self.offset_table):
            name = f'{str(i).zfill( len(str(len(self.offset_table)-1)))}'
            asset = Asset(name=name, offset=offset, size=self.sizes_list[i], data_ref=self.data_ref, index=i, father=self)
            #self.children.append(asset)
            self.children[i] = asset
    
    def generate_child(self, index:int, obj:Asset):
        '''Creates or overwrites a child asset.'''
        # TODO: Consider only inputting the 'obj' and let this method figure out the index
        # TODO: Maybe this method will be obsolete when all containers handle
        #   their asset lists internally
        if index < 0 or index >= len(self.children):
            raise ValueError(f'Invalid index position: {index}/{len(self.children)}')

        offset = self.offset_table[index]
        size = self.sizes_list[index]

        if isinstance(obj, Asset):
            obj.offset_father = offset
            obj.size = size
            obj.index_father = index
            obj.data_ref = self.data_ref
        # Containers are expected to already be fully initialized (offset_table/children)
        # by their own __init__, since they're constructed with their real offset/size upfront.

        new_asset_entry = obj

        self.children[index] = new_asset_entry  

    def generate_children(self):
        '''Generates all children with custom logic'''
        self.generate_generic_children() # Generate generic assets
        if self.asset_table == None:
            return # If no asset list, stop here.

        # Overwrite generic "Asset" children for typed dats in the asset table (like missions and aircraft)
        for dat_index in self.asset_table:
            index = int(dat_index)
            if index not in self.children:
                # Two legitimate reasons an index can be absent here:
                # (1) explicitly empty - the header has a real 0x00000000 entry
                #     at this slot (recorded in zero_offset_list), or
                # (2) out of range - this file's header is shorter than the
                #     asset table assumes (not every stage/mission uses every
                #     optional trailing slot; the table describes the maximum
                #     layout, not a fixed one), so the slot was never read at all.
                # Anything else missing is a real bug and should still surface
                # loudly, not be swallowed here.
                header_slots = getattr(self, 'header', None)
                out_of_range = header_slots is not None and index >= len(header_slots) - 1
                known_empty = index in getattr(self, 'zero_offset_list', [])
                if out_of_range or known_empty:
                    continue
                raise KeyError(
                    f'{self!r}: asset table references index {index}, but it is neither '
                    f'a populated child nor a known-empty/out-of-range header slot.'
                )

            raw_asset:Asset
            raw_asset = self.children[index]
            entry:dict = self.asset_table[dat_index]
            new_child = None
            
            asset_type = entry['type']
            #name = f'{str(i).zfill( len(str(len(self.offset_table))))}'

            index_zfill = str(index).zfill(len(str(len(self.asset_table)-1)))
            new_name = f'{index_zfill}_{asset_type}_{entry['name']}'

            #name=new_name
            size=raw_asset.size
            offset=raw_asset.offset_father
            data_ref=self.data_ref
            index=int(dat_index)
            father=self

            #ace_style = entry['ace_style']
            ace_style = entry.get('ace_style', '')

            if ace_style != '':
                # The style order (M/S/K etc.) recorded in the asset tables
                # above isn't fully trusted - death_the_d0g's own source doc
                # isn't internally consistent about it either (e.g. it lists
                # Juggernaut as S/M/K in one place and swaps it elsewhere).
                # Surface a visible reminder on every style-tagged slot to
                # manually verify (dialogue, other sources) rather than
                # silently trusting either source.
                new_name += f'_{ace_style} [CONFIRM ACE STYLE]'

            # Overwrite raw assets as stage assets
            # IMPORTANT! The '.dat' extension is not used consistently as the data structure I have described here;
            #   It's also used as a generic unknown file in the existing documentation.
            #   Trying to unpack a '.dat' that has a big number as its 'number of files' header, but does not use this number
            #   for this role might break unpackers, as they think they are parsing very a very long header that does not exist.
            #   We need a more specific nomenclature. I'll try to use '.unk' for unknown file formats from now on.
            #   My solution for now: Not considering every freaking unknown file as a .dat. Gotta diverge from the docs...
            if asset_type == 'dat': 
                new_child = DatFile(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
            if asset_type == 'mission_dat':
                new_child = DatMission(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father, ace_style=ace_style)
            elif asset_type == 'stage_dat':
                new_child = DatStage(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father, ace_style=ace_style)
            elif asset_type == 'free_flight_dat':
                new_child = DatFreeFlight(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father, ace_style=ace_style)
            elif asset_type == 'aircraft_dat':
                new_child = DatAircraft(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
            elif asset_type == 'aircraft_hangar_dat':
                new_child = DatAircraftHangar(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
            elif asset_type == 'hangar_dat':
                new_child = DatHangar(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
            elif asset_type == 'ambient_textures_dat':
                new_child = DatAmbientTextures(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
            elif asset_type == 'briefing_terrain_dat':
                new_child = DatBriefingTerrain(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
            elif asset_type == 'title_card_dat':
                new_child = DatTitleCardTexture(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
            #
            elif asset_type == 'gim':
                new_child = GIM(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
            elif asset_type == 'efd':
                new_child = EFD(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
            elif asset_type == 'acm':
                new_child = ACM(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
            elif asset_type == '': # If type is not known yet, make it a generic "Asset", but bring over table data.
                new_child = Asset(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)

            if new_child != None:
                self.generate_child(index=int(dat_index), obj=new_child)
            
    def __repr__(self):
        return f'CONTAINER | ({self.index_father})_{self.name} - size={self.size} - offset={self.offset_father}'


        

class DataPacAsset(Container):
    # TODO: Consider renaming this to 'DataPacAsset', as there are other
    #   .PAC files with different behaviors.
    def __init__(self, name:str, size:int, offset:int, data_ref:DataRefPac, index:int, father, asset_list:dict=None):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father, asset_list=asset_list)
        self.data_ref = data_ref # Not redundant. Receive specific DataRef class
        self.offset_table = data_ref.get_offset_table() # TODO: Get table from 'self.data_ref', not 'data_ref'
        
        self.init_offset_table()
        self.generate_children()
        pass
    
    def set_offset_table(self, offset_table: list):
        '''This method does nothing. It receives an unused param
            to comply with the Liskov Substitution Principle'''
        pass
    
    def init_offset_table(self):
        #self.offset_table = offset_table[:]
        self.offset_table = self.data_ref.get_offset_table() # TODO: Consider deleting. This line seems redundant
        ref_table = self.offset_table[:]
        ref_table.append(self.size)

        for i, offset in enumerate(ref_table):
            if i == len(ref_table)-1:
                break
            aux_size = ref_table[i+1] - ref_table[i]
            self.sizes_list.append(aux_size)




    def __repr__(self):
        return f'PAC_CONTAINER | {self.name} - size={self.size} - offset={self.offset_father}'

class DatFile(Container):
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father, asset_list:dict=None):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father, asset_list=asset_list)
        self.header:list = []
        self.zero_offset_list = []
        self.dat_type:str = ''
        self.sizes_list = []

        self.init_offset_table()
        self.generate_children()

    @property
    def is_empty(self) -> bool:
        '''True if this dat's header declares zero files - a real, valid
        placeholder state (e.g. a stage's unused sub-level slot, seen as a
        fixed-size file of a null file count followed by 0xCC filler), not
        an error. Not to be confused with an individual zero-offset slot
        inside a populated dat - this is about the dat itself having none.'''
        return bool(self.header) and self.header[0] == 0

    def set_offset_table(self, offset_table:list):
        '''This method does nothing. It receives an unused param
            to comply with the Liskov Substitution Principle'''
        pass

    def init_offset_table(self):
        offset_list = []
        file = self.data_ref
        #with open(dat_path, 'rb') as file:

        # self.data_ref is the single global buffer shared by the whole tree
        # (passed down unchanged from the root), so seeking needs the absolute
        # offset_ref (accumulated through the full father chain), not
        # offset_father (relative to just the immediate parent). Those two
        # happen to coincide for a DatFile whose parent is DATA_PAC directly
        # (offset_father(DATA_PAC) == 0), which is why this stayed hidden until
        # a DatFile ended up nested inside another one (e.g. a stage's own
        # embedded sub-level dat).
        file.seek(self.offset_ref)
        #curr_offset = self.offset
        # Read the raw data and null offset list from the .DAT
        read = file.read(4)
        #read = file.get_data(curr_offset, 4)
        number_of_files = int.from_bytes(read, byteorder="little")
        self.header.append(number_of_files)

        for offset_index in range(number_of_files):
            data = file.read(4)
            data_int = int.from_bytes(data, byteorder="little")

            if data_int != 0:
                offset_list.append(data_int)

            self.header.append(data_int)

        self.offset_table = offset_list

        
        ref_table = self.header[1:]
        ref_table.append(self.size)


        prev_offset = -1
        for offset in reversed(ref_table):
            if prev_offset == -1:
                prev_offset = offset
                continue
            if offset == 0:
                self.sizes_list.insert(0, 0)
                continue
            aux_size = prev_offset - offset
            self.sizes_list.insert(0, aux_size)
            prev_offset = offset

        # A slot is empty whenever its computed size is 0 - not just when its
        # raw offset is the literal 0x00000000 flag. Some sub-dats (e.g. the
        # nested stage dat at Glacial Skies' own slot 38) mark a zero-length
        # slot by repeating the *next* slot's offset instead of writing 0, so
        # the offset alone can't tell empty from populated; the computed size
        # (prev_offset - offset, from the pass above) can.
        self.zero_offset_list = [i for i, sz in enumerate(self.sizes_list) if sz == 0]

    def generate_generic_children(self):
        '''Generates generic children'''
        #sizes_index = 0 # index used for for 'sizes_list'
        ref_list = self.header[1:]
        for i, offset in enumerate(ref_list):
            if self.sizes_list[i] == 0: # Empty slot (literal 0 offset, or a zero-length file sharing the next slot's offset) - skip it. Indexes of the subfiles remain correct.
                continue
            name = f'{str(i).zfill( len(str(len(ref_list))))}'
            asset = Asset(name=name, offset=offset, size=self.sizes_list[i], data_ref=self.data_ref, index=i, father=self)
            #self.children.append(asset)
            self.children[i] = asset
            #sizes_index += 1


    
    def generate_child(self, index:int, obj:Asset):
        '''Creates or overwrites a child asset.
        TODO: Consider only inputting the 'obj' and let this method figure out the index'''
        #if index < 0 or index >= len(self.children):
        #    raise ValueError(f'Invalid index position: {index}/{len(self.children)}')

        #offset = self.offset_table[index]
        offset = (self.header[1:])[index]
        size = self.sizes_list[index]

        if isinstance(obj, Asset):
            obj.offset_father = offset
            obj.size = size
            obj.index_father = index
            obj.data_ref = self.data_ref
        # Containers are expected to already be fully initialized (offset_table/children)
        # by their own __init__, since they're constructed with their real offset/size upfront.

        new_asset_entry = obj
        self.children[index] = new_asset_entry  


    def __repr__(self):
        return f'DAT_CONTAINER | ({self.index_father})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset_father}'

class DatMission(DatFile):
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father, ace_style:str=''):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
        #self.generate_offset_table()
        self.dat_type:str = 'mission'
        self.ace_style = ace_style

    def __repr__(self):
        return f'MISSION_DAT | ({self.index_father})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset_father}'

class DatStage(DatFile):
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father, ace_style:str=''):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
        #self.generate_offset_table()
        self.dat_type:str = 'stage'
        self.ace_style = ace_style

    def __repr__(self):
        empty_note = ' [empty]' if self.is_empty else ''
        return f'STAGE_DAT | ({self.index_father})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset_father}{empty_note}'

class DatFreeFlight(DatMission):
    '''Per-stage Free Flight file - inherits DatMission (not DatFile
    directly) since it shares the same NOF-based header shape, and repeats
    the same M/S/K-tagged stage groups as DatMission/DatStage, so it needs
    the same ace_style plumbing.'''
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father, ace_style:str=''):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father, ace_style=ace_style)
        self.dat_type:str = 'free_flight'

    def __repr__(self):
        return f'FREE_FLIGHT_DAT | ({self.index_father})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset_father}'

class DatAircraft(DatFile):
    '''A flyable aircraft's .dat (one of 5 unlockable skin tiers - the tier
    is embedded in the name, not a separate field, since each aircraft slot
    is individually and unambiguously labeled in the source doc).'''
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
        self.dat_type:str = 'aircraft'

    def __repr__(self):
        return f'AIRCRAFT_DAT | ({self.index_father})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset_father}'

class DatAircraftHangar(DatFile):
    'A higher-detail aircraft model used for hangar display.'
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
        self.dat_type:str = 'aircraft_hangar'

    def __repr__(self):
        return f'AIRCRAFT_HANGAR_DAT | ({self.index_father})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset_father}'

class DatAmbientTextures(DatFile):
    '''A stage's ambient (skybox/weather) texture set - shadow cloud map,
    moon, clouds, star, lens flare, etc. (slot 19 of a stage .dat). Its own
    12-slot sub-table (ACZ_AMBIENT_TEXTURES_ASSET_LIST) names each GIM
    positionally (00-11), since which texture is which isn't identified
    yet.'''
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
        self.dat_type:str = 'ambient_textures'

    def __repr__(self):
        return f'AMBIENT_TEXTURES_DAT | ({self.index_father})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset_father}'

class DatHangar(DatFile):
    'A hangar building/environment asset (not per-aircraft).'
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
        self.dat_type:str = 'hangar'

    def __repr__(self):
        return f'HANGAR_DAT | ({self.index_father})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset_father}'

class DatBriefingTerrain(DatFile):
    'A per-mission briefing digitized terrain asset.'
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
        self.dat_type:str = 'briefing_terrain'

    def __repr__(self):
        return f'BRIEFING_TERRAIN_DAT | ({self.index_father})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset_father}'

class DatTitleCardTexture(DatFile):
    'A per-mission title card texture.'
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
        self.dat_type:str = 'title_card'

    def __repr__(self):
        return f'TITLE_CARD_DAT | ({self.index_father})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset_father}'

class GIM(Asset):
    'A GIM image file'
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father):
            super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)

    def __repr__(self):
            return f'GIM | ({self.index_father})_{self.name} - size={self.size} - offset={self.offset_father}'

class P3D(Asset):
    'IIRC, a P3D is a 3D object.'
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father):
            super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)

    def __repr__(self):
            return f'P3D | ({self.index_father})_{self.name} - size={self.size} - offset={self.offset_father}'

class EFD(Asset):
    'A stage particle effect configuration file'
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father):
            super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)

    def __repr__(self):
            return f'EFD | ({self.index_father})_{self.name} - size={self.size} - offset={self.offset_father}'

class ACM(Asset):
    'A 3D model file (seen used for stage trees/foliage)'
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father):
            super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)

    def __repr__(self):
            return f'ACM | ({self.index_father})_{self.name} - size={self.size} - offset={self.offset_father}'

def main():
    pass


if __name__ == '__main__':
    main()