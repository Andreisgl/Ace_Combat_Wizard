''' Classes for common assets. '''
import os
import json


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

        

        self.ACZ_DAT_ASSET_LIST = {
            '3': {'dat_type': 'stage', 'name': 'Glacial Skies', 'ace_style': ''},
            '4': {'dat_type': 'stage', 'name': 'Annex', 'ace_style': ''},
            '5': {'dat_type': 'stage', 'name': 'The Round Table', 'ace_style': 'M'},
            '6': {'dat_type': 'stage', 'name': 'The Round Table', 'ace_style': 'S'},
            '7': {'dat_type': 'stage', 'name': 'The Round Table', 'ace_style': 'K'},
            '8': {'dat_type': 'stage', 'name': 'Juggernaut', 'ace_style': 'M'},
            '9': {'dat_type': 'stage', 'name': 'Juggernaut', 'ace_style': 'S'},
            '10': {'dat_type': 'stage', 'name': 'Juggernaut', 'ace_style': 'K'},
            '11': {'dat_type': 'stage', 'name': 'Flicker of Hope', 'ace_style': ''},
            '12': {'dat_type': 'stage', 'name': 'Diapason', 'ace_style': ''},
            '13': {'dat_type': 'stage', 'name': 'Bastion', 'ace_style': ''},
            '14': {'dat_type': 'stage', 'name': 'Merlon', 'ace_style': 'M'},
            '15': {'dat_type': 'stage', 'name': 'Merlon', 'ace_style': 'S'},
            '16': {'dat_type': 'stage', 'name': 'Merlon', 'ace_style': 'K'},
            '17': {'dat_type': 'stage', 'name': 'Sword of Annihilation', 'ace_style': ''},
            '18': {'dat_type': 'stage', 'name': 'Mayhem', 'ace_style': 'M'},
            '19': {'dat_type': 'stage', 'name': 'Mayhem', 'ace_style': 'S'},
            '20': {'dat_type': 'stage', 'name': 'Mayhem', 'ace_style': 'K'},
            '21': {'dat_type': 'stage', 'name': 'The Inferno', 'ace_style': ''},
            '22': {'dat_type': 'stage', 'name': 'The Stage of the Apocalypse', 'ace_style': ''},
            '23': {'dat_type': 'stage', 'name': 'Lying in Deceit', 'ace_style': ''},
            '24': {'dat_type': 'stage', 'name': 'The Final Overture', 'ace_style': 'M'},
            '25': {'dat_type': 'stage', 'name': 'The Final Overture', 'ace_style': 'S'},
            '26': {'dat_type': 'stage', 'name': 'The Final Overture', 'ace_style': 'K'},
            '27': {'dat_type': 'stage', 'name': 'The Talon of Ruin', 'ace_style': ''},
            '28': {'dat_type': 'stage', 'name': 'The Demon of the Round Table', 'ace_style': 'M'},
            '29': {'dat_type': 'stage', 'name': 'The Demon of the Round Table', 'ace_style': 'S'},
            '30': {'dat_type': 'stage', 'name': 'The Demon of the Round Table', 'ace_style': 'K'},
            '31': {'dat_type': 'stage', 'name': 'The Valley of Kings', 'ace_style': ''},
            '32': {'dat_type': 'stage', 'name': 'ZERO', 'ace_style': ''},
            '33': {'dat_type': 'stage', 'name': 'The Gauntlet', 'ace_style': ''},
            #
            '43': {'dat_type': 'stage', 'name': 'Valais Air Force Base', 'ace_style': ''},
            #
            '251': {'dat_type': 'mission', 'name': 'Glacial Skies', 'ace_style': ''},
            '252': {'dat_type': 'mission', 'name': 'Annex', 'ace_style': ''},
            '253': {'dat_type': 'mission', 'name': 'The Round Table', 'ace_style': 'M'},
            '254': {'dat_type': 'mission', 'name': 'The Round Table', 'ace_style': 'S'},
            '255': {'dat_type': 'mission', 'name': 'The Round Table', 'ace_style': 'K'},
            '256': {'dat_type': 'mission', 'name': 'Juggernaut', 'ace_style': 'M'},
            '257': {'dat_type': 'mission', 'name': 'Juggernaut', 'ace_style': 'S'},
            '258': {'dat_type': 'mission', 'name': 'Juggernaut', 'ace_style': 'K'},
            '259': {'dat_type': 'mission', 'name': 'Flicker of Hope', 'ace_style': ''},
            '260': {'dat_type': 'mission', 'name': 'Diapason', 'ace_style': ''},
            '261': {'dat_type': 'mission', 'name': 'Bastion', 'ace_style': ''},
            '262': {'dat_type': 'mission', 'name': 'Merlon', 'ace_style': 'M'},
            '263': {'dat_type': 'mission', 'name': 'Merlon', 'ace_style': 'S'},
            '264': {'dat_type': 'mission', 'name': 'Merlon', 'ace_style': 'K'},
            '265': {'dat_type': 'mission', 'name': 'Sword of Annihilation', 'ace_style': ''},
            '266': {'dat_type': 'mission', 'name': 'Mayhem', 'ace_style': 'M'},
            '267': {'dat_type': 'mission', 'name': 'Mayhem', 'ace_style': 'S'},
            '268': {'dat_type': 'mission', 'name': 'Mayhem', 'ace_style': 'K'},
            '269': {'dat_type': 'mission', 'name': 'The Inferno', 'ace_style': ''},
            '270': {'dat_type': 'mission', 'name': 'The Stage of the Apocalypse', 'ace_style': ''},
            '271': {'dat_type': 'mission', 'name': 'Lying in Deceit', 'ace_style': ''},
            '272': {'dat_type': 'mission', 'name': 'The Final Overture', 'ace_style': 'M'},
            '273': {'dat_type': 'mission', 'name': 'The Final Overture', 'ace_style': 'S'},
            '274': {'dat_type': 'mission', 'name': 'The Final Overture', 'ace_style': 'K'},
            '275': {'dat_type': 'mission', 'name': 'The Talon of Ruin', 'ace_style': ''},
            '276': {'dat_type': 'mission', 'name': 'The Demon of the Round Table', 'ace_style': 'M'},
            '277': {'dat_type': 'mission', 'name': 'The Demon of the Round Table', 'ace_style': 'S'},
            '278': {'dat_type': 'mission', 'name': 'The Demon of the Round Table', 'ace_style': 'K'},
            '279': {'dat_type': 'mission', 'name': 'The Valley of Kings', 'ace_style': ''},
            '280': {'dat_type': 'mission', 'name': 'ZERO', 'ace_style': ''},
            '281': {'dat_type': 'mission', 'name': 'The Gauntlet', 'ace_style': ''}
        }

        # Asset creation:
        self.DATA_PAC = DataPacAsset(name='DATA.PAC', size=os.stat(pac_path).st_size, offset = 0, data_ref=self._DATA_PAC_REF, index=0, father=self, asset_list=self.ACZ_DAT_ASSET_LIST)
        
        
        
        pass

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

    def get_raw_data(self) -> bytes:
        '''Returns this asset's own raw bytes, read from its data reference.'''
        return self.data_ref.get_data(self.offset_ref, self.size)

    def __repr__(self):
        return f'ASSET | ({self.index_father})_{self.name} - size={self.size} - offset={self.offset_father}'


class Container(Asset): # Abstract
    '''A simple container that has generic children based on a offset table'''
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
        self.offset_table = []
        self.sizes_list:list = []
        self.children = dict()
    
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

    def generate_children(self):
        '''Generates all children of the container'''
        for i, offset in enumerate(self.offset_table):
            name = f'{str(i).zfill( len(str(len(self.offset_table))))}'
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

    def __repr__(self):
        return f'CONTAINER | ({self.index_father})_{self.name} - size={self.size} - offset={self.offset_father}'

class ListedContainer(Container): # Abstract
    '''A container that supports an assetlist to name and type its contents'''
    def __init__(self, name:str, size:int, offset:int, data_ref:DataRefPac, index:int, father, asset_list:dict=None):
            super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
            self.asset_list:dict = asset_list

    def generate_generic_children(self):
        '''Generate generic "Asset" children.'''
        # Repurpose the simple generic child generation in this new signature
        super().generate_children()

    def generate_children(self):
        '''Generates all children of the PAC file'''
        self.generate_generic_children() # Generate generic assets
        if self.asset_list == None:
            return # If no asset list, stop here.
        else:
            pass
            # Custom per-type child generation logic here.
            # This is an abstract class, so it does not need logic

        

class DataPacAsset(ListedContainer):
    # TODO: Consider renaming this to 'DataPacAsset', as there are other
    #   .PAC files with different behaviors.
    def __init__(self, name:str, size:int, offset:int, data_ref:DataRefPac, index:int, father, asset_list:dict=None):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
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

    def generate_children(self):
        '''Generates all children of the PAC file'''
        super().generate_generic_children() # Generate generic assets
        if self.asset_list == None:
            return # If no asset list, stop here.
            

        # Overwrite generic "Asset" children for typed dats in the lookup table (like missions and aircraft)
        for dat_index in self.asset_list:
            raw_asset:Asset
            raw_asset = self.children[int(dat_index)]
            entry:dict = self.asset_list[dat_index]
            new_child = None
            
            dat_type = entry['dat_type']
            new_name = f'{dat_type}_{entry['name']}'

            #name=new_name
            size=raw_asset.size
            offset=raw_asset.offset_father
            data_ref=self.data_ref
            index=int(dat_index)
            father=self

            #ace_style = entry['ace_style']
            ace_style = entry.get('ace_style', '')

            if ace_style != '':
                new_name += f'_{ace_style}'

            if entry['dat_type'] == 'mission': # Overwrite raw assets as mission assets
                new_child = DatMission(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father, ace_style=ace_style)
            elif entry['dat_type'] == 'stage': # Overwrite raw assets as stage assets
                new_child = DatStage(name=new_name, size=size, offset=offset, data_ref=data_ref, index=index, father=father, ace_style=ace_style)

            self.generate_child(index=int(dat_index), obj=new_child)
        pass




    def __repr__(self):
        return f'PAC_CONTAINER | {self.name} - size={self.size} - offset={self.offset_father}'

class DatFile(ListedContainer):
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
        self.header:list = []
        self.zero_offset_list = []
        self.dat_type:str = ''
        self.sizes_list = []

        self.init_offset_table()
        self.generate_children()


    def set_offset_table(self, offset_table:list):
        '''This method does nothing. It receives an unused param
            to comply with the Liskov Substitution Principle'''
        pass

    def init_offset_table(self):   
        offset_list = []
        zero_offset_list = []
        file = self.data_ref
        #with open(dat_path, 'rb') as file:

        file.seek(self.offset_father)
        #curr_offset = self.offset
        # Read the raw data and null offset list from the .DAT
        read = file.read(4)            
        #read = file.get_data(curr_offset, 4)
        number_of_files = int.from_bytes(read, byteorder="little")
        self.header.append(number_of_files)
        
        for offset_index in range(number_of_files):
            #curr_offset += 4
            data = file.read(4)
            #data = file.get_data(curr_offset, 4)
            data_int = int.from_bytes(data, byteorder="little")
            
            if data_int != 0:
                offset_list.append(data_int)
            else:
                zero_offset_list.append(offset_index)

            self.header.append(data_int)
        
        self.offset_table = offset_list
        self.zero_offset_list = zero_offset_list
        #return offset_list, zero_offset_list

        ###

        #self.offset_table = offset_table[:]
        ref_table = self.header[1:]
        ref_table.append(self.size)

    
        #for i, offset in enumerate(ref_table):
        #    if i == len(ref_table)-1:
        #        break
        #    aux_size = ref_table[i+1] - ref_table[i]
        #    self.sizes_list.append(aux_size)
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

    def generate_children(self):
        '''Generates all children of the dat file'''
        #sizes_index = 0 # index used for for 'sizes_list'
        ref_list = self.header[1:]
        for i, offset in enumerate(ref_list):
            if offset == 0: # If offset is an empty entry skip it. Its offset will be skipped and indexes of the subfiles will be correct.
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
        self.zero_offset_list = []
        #self.generate_offset_table()
        self.dat_type:str = 'mission'
        self.ace_style = ace_style

    def __repr__(self):
        return f'MISSION_DAT | ({self.index_father})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset_father}'

class DatStage(DatFile):
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, father, ace_style:str=''):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, father=father)
        self.zero_offset_list = []
        #self.generate_offset_table()
        self.dat_type:str = 'stage'
        self.ace_style = ace_style

    def generate_children(self):
        '''Generates all children of the stage dat file'''
        #sizes_index = 0 # index used for for 'sizes_list'
        ref_list = self.header[1:]
        for i, offset in enumerate(ref_list):
            if offset == 0: # If offset is an empty entry skip it. Its offset will be skipped and indexes of the subfiles will be correct.
                continue
            name = f'{str(i).zfill( len(str(len(ref_list))))}'
            asset = Asset(name=name, offset=offset, size=self.sizes_list[i], data_ref=self.data_ref, index=i, father=self)
            #self.children.append(asset)
            self.children[i] = asset
            #sizes_index += 1

    def __repr__(self):
        return f'STAGE_DAT | ({self.index_father})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset_father}'

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



def main():
    pass
#    tbl_path = 'DATA.TBL'
#    pac_path = 'DATA.PAC'
#    
#
#    raw_datapac_data = b''
#    with open(pac_path, 'rb') as file:
#        raw_datapac_data = file.read()
#    
#    raw_datatbl_data = b''
#    with open(tbl_path, 'rb') as file:
#        raw_datatbl_data = file.read()
#
#    DATA_TBL_REF = DataRefTbl(name='datatbl_ref', raw_data=raw_datatbl_data)
#    DATA_PAC_REF = DataRefPac(name='datapac_ref', raw_data=raw_datapac_data, tbl_ref=DATA_TBL_REF)
#
#    
#    DATA_PAC = DataPacAsset(name='DATA.PAC', size=os.stat(pac_path).st_size, offset = 0, data_ref=DATA_PAC_REF, index=0, father=None)
#    #DATA_PAC.init_offset_table()
#
#    
#    DAT_ASSET_LIST = {
#        '251': {'dat_type': 'mission', 'name': 'Glacial Skies', 'ace_style': 'all'},
#        '252': {'dat_type': 'mission', 'name': 'Annex', 'ace_style': 'all'},
#        '253': {'dat_type': 'mission', 'name': 'The Round Table', 'ace_style': 'M'},
#        '254': {'dat_type': 'mission', 'name': 'The Round Table', 'ace_style': 'S'},
#        '255': {'dat_type': 'mission', 'name': 'The Round Table', 'ace_style': 'K'},
#        '256': {'dat_type': 'mission', 'name': 'Juggernaut', 'ace_style': 'M'},
#        '257': {'dat_type': 'mission', 'name': 'Juggernaut', 'ace_style': 'S'},
#        '258': {'dat_type': 'mission', 'name': 'Juggernaut', 'ace_style': 'K'},
#        '259': {'dat_type': 'mission', 'name': 'Flicker of Hope', 'ace_style': 'all'},
#        '260': {'dat_type': 'mission', 'name': 'Diapason', 'ace_style': 'all'},
#        '261': {'dat_type': 'mission', 'name': 'Bastion', 'ace_style': 'all'},
#        '262': {'dat_type': 'mission', 'name': 'Merlon', 'ace_style': 'M'},
#        '263': {'dat_type': 'mission', 'name': 'Merlon', 'ace_style': 'S'},
#        '264': {'dat_type': 'mission', 'name': 'Merlon', 'ace_style': 'K'},
#        '265': {'dat_type': 'mission', 'name': 'Sword of Annihilation', 'ace_style': 'all'},
#        '266': {'dat_type': 'mission', 'name': 'Mayhem', 'ace_style': 'M'},
#        '267': {'dat_type': 'mission', 'name': 'Mayhem', 'ace_style': 'S'},
#        '268': {'dat_type': 'mission', 'name': 'Mayhem', 'ace_style': 'K'},
#        '269': {'dat_type': 'mission', 'name': 'The Inferno', 'ace_style': 'all'},
#        '270': {'dat_type': 'mission', 'name': 'The Stage of the Apocalypse', 'ace_style': 'all'},
#        '271': {'dat_type': 'mission', 'name': 'Lying in Deceit', 'ace_style': 'all'},
#        '272': {'dat_type': 'mission', 'name': 'The Final Overture', 'ace_style': 'M'},
#        '273': {'dat_type': 'mission', 'name': 'The Final Overture', 'ace_style': 'S'},
#        '274': {'dat_type': 'mission', 'name': 'The Final Overture', 'ace_style': 'K'},
#        '275': {'dat_type': 'mission', 'name': 'The Talon of Ruin', 'ace_style': 'all'},
#        '276': {'dat_type': 'mission', 'name': 'The Demon of the Round Table', 'ace_style': 'M'},
#        '277': {'dat_type': 'mission', 'name': 'The Demon of the Round Table', 'ace_style': 'S'},
#        '278': {'dat_type': 'mission', 'name': 'The Demon of the Round Table', 'ace_style': 'K'},
#        '279': {'dat_type': 'mission', 'name': 'The Valley of Kings', 'ace_style': 'all'},
#        '280': {'dat_type': 'mission', 'name': 'ZERO', 'ace_style': 'all'},
#        '281': {'dat_type': 'mission', 'name': 'The Gauntlet', 'ace_style': 'all'}
#    }
#
#
#    for dat_index in DAT_ASSET_LIST:
#        raw_asset:Asset
#        raw_asset = DATA_PAC.children[int(dat_index)]
#        entry = DAT_ASSET_LIST[dat_index]
#        new_child = None
#        
#        dat_type = entry['dat_type']
#        new_name = f'{dat_type}_{entry['name']}'
#        
#        if entry['dat_type'] == 'mission':
#            ace_style = entry['ace_style']
#            new_child = DatMission(name=new_name, size=-1, offset=-1, data_ref=DATA_PAC.data_ref, index=int(dat_index), father=DATA_PAC, ace_style=ace_style, deferred_children=True)
#            DATA_PAC.generate_child(index=int(dat_index), obj=new_child)
#        #elif .... other classes...
#
#        
#
#
#        #DATA_PAC.generate_child(int(dat_index), new_name, child_class)
#        #DATA_PAC.generate_child(int(dat_index), new_name, child_class)
#
#        print(DATA_PAC.children[int(dat_index)])
#
#    
#    pass


if __name__ == '__main__':
    main()