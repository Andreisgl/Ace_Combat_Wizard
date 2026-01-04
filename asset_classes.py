''' Classes for common assets. '''
import os

class DataReference():
    ''' This class hold the actual data '''
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
        return max(0, self.size - self._cursor)

    def get_data(self, offset: int, length: int) -> bytes:
        if length <= 0:
            return b''

        if offset < 0:
            return b''

        if offset >= self.size:
            return b''

        end = offset + length
        return self._raw_data[offset:end]



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
        self.sizes_list:list = [] # TODO: Check if this is used
        self.children = dict()
       
    def init_offset_table(self, offset_table:list):
        self.offset_table = offset_table[:]
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
    
    def generate_child(self, index:int, name:str, asset_class:type[Asset]):
        '''Creates or overwrites a child asset.'''
        if index < 0 or index >= len(self.children):
            raise ValueError(f'Invalid index position: {index}/{len(self.children)}')
        
        offset = self.offset_table[index]
        size = self.sizes_list[index]

        new_asset = asset_class(name=name, size=size, offset=offset, data_ref=self.data_ref, index=index)
        new_asset_entry = {index: new_asset}

        self.children[index] = new_asset_entry  

    def __repr__(self):
        return f'CONTAINER | ({self.index})_{self.name} - size={self.size} - offset={self.offset}'

class PacFile(Container):
    # TODO: Consider passing DATA.TBL data ref to this class on init.
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index)
        #self.offset_table = []
        #self.sizes_list:list = []
        #self.children = []
       
    def init_offset_table(self, offset_table:list):
        self.offset_table = offset_table[:]
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
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index)
        self.zero_offset_list = []
        #self.generate_offset_table()
        self.dat_type:str = ''
        self.sizes_list = []

        self.init_offset_table()
        self.generate_children()

    
    def init_offset_table(self): #### TODO: Generate sizes_list
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

    #def generate_children(self):
    #        name = f'{str(i).zfill( len(str(len(ref_table))) )}.asset' # TODO: use len(table) for zfill
    #        container = Asset(name=name, offset=offset, size=aux_size, data_ref=self.data_ref, index=i)
    #        self.children.append(container)
    
    def __repr__(self):
        return f'DAT_CONTAINER | ({self.index})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset}'

class DatMission(DatFile):
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index)
        self.zero_offset_list = []
        #self.generate_offset_table()
        self.dat_type:str = 'mission'

    def __repr__(self):
        return f'MISSION_DAT | ({self.index})_{self.name} - dat_type={self.dat_type} - size={self.size} - offset={self.offset}'


def get_tbl_offset_table(tbl_path:str) -> list:
    # Returns the offset table and sizes from a .TBL file
    offset_list = []
    size_list = []
    with open(tbl_path, 'rb') as tbl_file:
        tbl_nof = int.from_bytes(tbl_file.read(4), byteorder="little")
        tbl_file.seek(8)
        for _ in range(tbl_nof):
            offset_list.append(int.from_bytes(tbl_file.read(4), byteorder="little"))
            size_list.append(int.from_bytes(tbl_file.read(4), byteorder="little"))
    return offset_list





    

def get_tbl_offset_table_dataref(data:bytes):
    offset_list = []
    


def main():
    tbl_path = 'DATA.TBL'
    pac_path = 'DATA.PAC'
    tbl_offset_table = get_tbl_offset_table(tbl_path)

    raw_datapac_data = b''
    with open(pac_path, 'rb') as file:
        raw_datapac_data = file.read()

    DATA_PAC_REF = DataReference(name='datapac_ref', raw_data=raw_datapac_data)
    
    DATA_PAC = PacFile(name='DATA.PAC', size=os.stat(pac_path).st_size, offset = 0, data_ref=DATA_PAC_REF, index=0)
    DATA_PAC.init_offset_table(tbl_offset_table)

    
    DAT_ASSET_LIST = {
        '251': {'dat_type': 'mission', 'name': 'Glacial Skies', 'ace_style': 'all'},
        '252': {'dat_type': 'mission', 'name': 'Annex', 'ace_style': 'all'},
        '253': {'dat_type': 'mission', 'name': 'The Round Table', 'ace_style': 'M'},
        '254': {'dat_type': 'mission', 'name': 'The Round Table', 'ace_style': 'S'},
        '255': {'dat_type': 'mission', 'name': 'The Round Table', 'ace_style': 'K'},
    }

    DAT_CLASS_LOOKUP_TABLE = {
        'mission': DatMission
    }

    for dat_index in DAT_ASSET_LIST:
        raw_asset:Asset
        raw_asset = DATA_PAC.children[int(dat_index)]
        entry = DAT_ASSET_LIST[dat_index]
        
        type = entry['dat_type']
        new_name = f'{type}_{entry['name']}'
        #size = raw_asset.size
        #offset = raw_asset.offset
        #data_ref = raw_asset.data_ref

        #dat = DatFile(name=new_name, size=size, offset=offset, data_ref=data_ref, index=int(dat_index))
        
        DATA_PAC.generate_child(int(dat_index), new_name, DatFile)

        print(DATA_PAC.children[int(dat_index)])

        #aux_dat = DATA_PAC.children[251]

        #dat.generate_child(index=0, name='', asset_class=Container)

    
    pass


if __name__ == '__main__':
    main()