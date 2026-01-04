''' Classes for common assets. '''
import os

class DataReference():
    ''' This class hold the actual data '''
    def __init__(self, name:str, raw_data:bytes):
        self._raw_data:bytes = raw_data
        self.size = len(raw_data)

        self._cursor:int = 0
    
    def read(self, size) -> bytes:
        remaining_length = self.get_remaining_length()
        if remaining_length == 0:
            return b''
        elif remaining_length < 0:
            return b''
        
        if size > remaining_length:
            self._cursor += remaining_length
            return self.get_data(offset=self._cursor, length=remaining_length)
        else:
            self._cursor += size
            return self.get_data(offset=self._cursor, length=size)
        
    def tell(self):
        return self._cursor
    
    def seek(self, pos:int):
        if not (0 < pos < self.size):
            return self._cursor
        
        self._cursor = pos
        return self._cursor

    def get_remaining_length(self):
        result = self.size - self._cursor
        if result < 0:
            self._cursor = self.size-1
            return 0
        return result

    def get_data(self, offset:int, length:int) -> bytes:
        start_address = offset
        end_address_exclusive = start_address + length
        output_data = b''

        if start_address >= end_address_exclusive:
            return b''
        
        if start_address > self.size-1:
            return b''
        if end_address_exclusive > self.size-1:
            return b''
        #
        if start_address < 0:
            return b''
        if end_address_exclusive <= 0:
            return b''
        
        output_data = self._raw_data[start_address:end_address_exclusive]
        return output_data


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
        self.children = []
       
    def init_offset_table(self, offset_table:list):
        self.offset_table = offset_table[:]
        ref_table = self.offset_table[:]
        ref_table.append(self.size)

        for i, offset in enumerate(ref_table):
            if i == len(ref_table)-1:
                break
            aux_size = ref_table[i+1] - ref_table[i]
            self.sizes_list.append(aux_size)

            name = f'{str(i).zfill( len(str(len(ref_table))) )}'
            container = Asset(name=name, offset=offset, size=aux_size, data_ref=self.data_ref, index=i)
            self.children.append(container)
    
    def __repr__(self):
        return f'CONTAINER | ({self.index})_{self.name} - size={self.size} - offset={self.offset}'



class PacFile(Container):
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index)
        self.offset_table = []
        self.sizes_list:list = []
        self.children = []
       
    def init_offset_table(self, offset_table:list):
        self.offset_table = offset_table[:]
        ref_table = self.offset_table[:]
        ref_table.append(self.size)

        for i, offset in enumerate(ref_table):
            if i == len(ref_table)-1:
                break
            aux_size = ref_table[i+1] - ref_table[i]
            self.sizes_list.append(aux_size)

            name = f'{str(i).zfill( len(str(len(ref_table))) ) }.dat'
            container = DatFile(name=name, offset=offset, size=aux_size, data_ref=self.data_ref, index=i)
            self.children.append(container)
    
    def __repr__(self):
        return f'PAC_CONTAINER | {self.name} - size={self.size} - offset={self.offset}'
    


class DatFile(Container):
    def __init__(self, name:str, size:int, offset:int, data_ref:DataReference, index:int):
        super().__init__(name=name, size=size, offset=offset, data_ref=data_ref, index=index)
        self.zero_offset_list = []
        #self.generate_offset_table()
    
    def generate_offset_table(self): #### not done
        offset_list = []
        zero_offset_list = []
        file = self.data_ref
        #with open(dat_path, 'rb') as file:

        #file.seek(dat_obj.offset)
        curr_offset = self.offset
        # Read the raw data and null offset list from the .DAT
        #read = file.read(4)            
        read = file.get_data(curr_offset, 4)
        number_of_files = int.from_bytes(read, byteorder="little")
        
        for offset_index in range(number_of_files):
            curr_offset += 4
            #data = file.read(4)
            data = file.get_data(curr_offset, 4)
            data_int = int.from_bytes(data, byteorder="little")
            
            if data_int != 0:
                offset_list.append(data_int)
            else:
                zero_offset_list.append(offset_index)
        
        self.offset_table = offset_list
        self.zero_offset_list = zero_offset_list
        #return offset_list, zero_offset_list

    def generate_children(self):
        #self.offset_table = offset_table[:]
        ref_table = self.offset_table[:]
        ref_table.append(self.size)

        for i, offset in enumerate(ref_table):
            if i == len(ref_table)-1:
                break
            aux_size = ref_table[i+1] - ref_table[i]
            self.sizes_list.append(aux_size)

            name = f'{str(i).zfill( len(str(len(ref_table))) )}.asset' # TODO: use len(table) for zfill
            container = DatFile(name=name, offset=offset, size=aux_size, data_ref=self.data_ref, index=i)
            self.children.append(container)
    
    def __repr__(self):
        return f'DAT_CONTAINER | ({self.index})_{self.name} - size={self.size} - offset={self.offset}'



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

    aux_dat = DATA_PAC.children[251]

    
    pass


if __name__ == '__main__':
    main()