''' Classes for common assets. '''
import os

class Container():
    def __init__(self, name:str, size:int, offset, offset_table:list = []):
        self.name = name
        self.offset = offset # Offset from its father container.
        self.size = size

        self.offset_table = offset_table
        self.sizes_list:list = []
        self.children = []
       
        ref_table = offset_table[:]
        ref_table.append(size)

        for i, offset in enumerate(ref_table):
            if i == len(ref_table)-1:
                break
            aux_size = ref_table[i+1] - ref_table[i]
            self.sizes_list.append(aux_size)

            name = f'{str(i).zfill(4)}.dat'
            container = Container(name=name, offset=offset, size=aux_size)
            self.children.append(container)
    
    def __repr__(self):
        return f'Container | {self.name} - size={self.size} - offset={self.offset}'

class DATA_PAC(Container):
    def __init__(self, size:int, offset, offset_table:list = []):
        pass

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


def main():
    tbl_path = 'DATA.TBL'
    pac_path = 'DATA.PAC'
    tbl_offset_table = []
    sizes_list = []
    tbl_offset_table = get_tbl_offset_table(tbl_path)
    DATA_PAC = Container(name='DATA.PAC', size = os.stat(pac_path).st_size, offset = 0, offset_table=tbl_offset_table)

    pass


if __name__ == '__main__':
    main()