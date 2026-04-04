''' Classes for common assets. '''
import os

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
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int):
        self.name = name
        self.size = size
        self.offset = offset # Offset from its father container.
        self.index = index # Offset from its father container.
        self.data_ref = data_ref
        
    def __repr__(self):
        return f'ASSET | ({self.index})_{self.name} - size={self.size} - offset={self.offset}'

class Container(Asset):
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index)
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
            asset = Asset(name=name, offset=offset, size=self.sizes_list[i], data_ref=self.data_ref, index=i)
            #self.children.append(asset)
            self.children[i] = asset
    
    def generate_child(self, index:int, obj:Asset):
        '''Creates or overwrites a child asset.'''
        if index < 0 or index >= len(self.children):
            raise ValueError(f'Invalid index position: {index}/{len(self.children)}')

        offset = self.offset_table[index]
        size = self.sizes_list[index]

        if isinstance(obj, Asset):
            obj.offset = offset
            obj.size = size
            obj.index = index
            obj.data_ref = self.data_ref
        if isinstance(obj, Container):
            obj.init_offset_table()
            obj.generate_children()

        new_asset_entry = {index: obj}

        self.children[index] = new_asset_entry  

    def __repr__(self):
        return f'CONTAINER | ({self.index})_{self.name} - size={self.size} - offset={self.offset}'

class DataPacAsset(Container):
    # TODO: Consider renaming this to 'DataPacAsset', as there are other
    #   .PAC files with different behaviors.
    def __init__(self, name:str, size:int, offset:int, data_ref:DataRefPac, index:int):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index)
        self.data_ref = data_ref # Not redundant. Receive specific DataRef class
        self.offset_table = data_ref.get_offset_table()
        self.init_offset_table()
    
    def set_offset_table(self, offset_table: list):
        '''This method does nothing. It receives an unused param
            to comply with the Liskov Substitution Principle'''
        pass
    
    def init_offset_table(self):
        #self.offset_table = offset_table[:]
        self.offset_table = self.data_ref.get_offset_table()
        ref_table = self.offset_table[:]
        ref_table.append(self.size)

        for i, offset in enumerate(ref_table):
            if i == len(ref_table)-1:
                break
            aux_size = ref_table[i+1] - ref_table[i]
            self.sizes_list.append(aux_size)
        
        self.generate_children()
    
    def __repr__(self):
        return f'PAC_CONTAINER | {self.name} - size={self.size} - offset={self.offset}'

class DatFile(Container):
    ''' 'deferred_children' means that the children won't be created right on instace creation.
        This means that they will only be created manually.'''
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, deferred_children:bool=False):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index)
        self.zero_offset_list = []
        self.dat_type:str = ''
        self.sizes_list = []

        if not deferred_children:
            self.init_offset_table()
            self.generate_children()

    
    def set_offset_table(self, offset_table: list):
        '''This method does nothing. It receives an unused param
            to comply with the Liskov Substitution Principle'''
        pass

    def init_offset_table(self):
        offset_list = []
        zero_offset_list = []
        file = self.data_ref
        #with open(dat_path, 'rb') as file:

        file.seek(self.offset)
        #curr_offset = self.offset
        # Read the raw data and null offset list from the .DAT
        read = file.read(4)            
        #read = file.get_data(curr_offset, 4)
        number_of_files = int.from_bytes(read, byteorder="little")
        
        for offset_index in range(number_of_files):
            #curr_offset += 4
            data = file.read(4)
            #data = file.get_data(curr_offset, 4)
            data_int = int.from_bytes(data, byteorder="little")
            
            if data_int != 0:
                offset_list.append(data_int)
            else:
                zero_offset_list.append(offset_index)
        
        self.offset_table = offset_list
        self.zero_offset_list = zero_offset_list
        #return offset_list, zero_offset_list

        ###

        #self.offset_table = offset_table[:]
        ref_table = self.offset_table[:]
        ref_table.append(self.size)

    
        for i, offset in enumerate(ref_table):
            if i == len(ref_table)-1:
                break
            aux_size = ref_table[i+1] - ref_table[i]
            self.sizes_list.append(aux_size)
    
    def __repr__(self):
        return f'DAT_CONTAINER | ({self.index})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset}'

class DatMission(DatFile):
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int, ace_style:str='', deferred_children:bool=False):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index, deferred_children=deferred_children)
        self.zero_offset_list = []
        #self.generate_offset_table()
        self.dat_type:str = 'mission'
        self.ace_style = ace_style

    def __repr__(self):
        return f'MISSION_DAT | ({self.index})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset}'





def main():
    tbl_path = 'DATA.TBL'
    pac_path = 'DATA.PAC'
    

    raw_datapac_data = b''
    with open(pac_path, 'rb') as file:
        raw_datapac_data = file.read()
    
    raw_datatbl_data = b''
    with open(tbl_path, 'rb') as file:
        raw_datatbl_data = file.read()

    DATA_TBL_REF = DataRefTbl(name='datatbl_ref', raw_data=raw_datatbl_data)
    DATA_PAC_REF = DataRefPac(name='datapac_ref', raw_data=raw_datapac_data, tbl_ref=DATA_TBL_REF)

    DATA_PAC = DataPacAsset(name='DATA.PAC', size=os.stat(pac_path).st_size, offset = 0, data_ref=DATA_PAC_REF, index=0)
    #DATA_PAC.init_offset_table()

    
    DAT_ASSET_LIST = {
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


    for dat_index in DAT_ASSET_LIST:
        raw_asset:Asset
        raw_asset = DATA_PAC.children[int(dat_index)]
        entry = DAT_ASSET_LIST[dat_index]
        new_child = None
        
        dat_type = entry['dat_type']
        new_name = f'{dat_type}_{entry['name']}'
        
        if entry['dat_type'] == 'mission':
            ace_style = entry['ace_style']
            new_child = DatMission(name=new_name, size=-1, offset=-1, data_ref=DATA_PAC.data_ref, index=int(dat_index), ace_style=ace_style, deferred_children=True)
            DATA_PAC.generate_child(index=int(dat_index), obj=new_child)
        #elif .... other classes...

        


        #DATA_PAC.generate_child(int(dat_index), new_name, child_class)
        #DATA_PAC.generate_child(int(dat_index), new_name, child_class)

        print(DATA_PAC.children[int(dat_index)])

    
    pass


if __name__ == '__main__':
    main()