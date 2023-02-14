# This module is responsible for extracting and rebuilding .PAC files.
# Code based on the "ACZ_PAC_TOOLS.2" by Death_the_d0g (deaththed0g @ Github, Death_the_d0g @ Twitter)

def extraction(pac_file, tbl_file):
    val = 0
    f_n = 0
    f_offset = 8
    offset_list = []
    size_list = []
    file_data_list = []
    file_name_list = []

    tbl_file.seek(0, 0)
    tbl_nof = int.from_bytes(tbl_file.read(4), byteorder = "little")
    for f in range(tbl_nof):
        tbl_file.seek(f_offset, 0)
        offset_list.append(int.from_bytes(tbl_file.read(4), byteorder = "little"))
        f_offset = f_offset + 4
        tbl_file.seek(f_offset, 0)
        size_list.append(int.from_bytes(tbl_file.read(4), byteorder = "little"))
        f_offset = f_offset + 4
    for f in range(tbl_nof):
        file_name_list.append(str(f).zfill(4) + ".dat")

        pac_file.seek(offset_list[val])
        data = pac_file.read(size_list[val])
        file_data_list.append(data)

        print("file:", file_name_list[f], "offset:", hex(offset_list[val]), "size:", size_list[val])
        val = val + 1
        #f_n = f_n + 1
    return file_data_list, file_name_list

def rebuilding(dat_data_list):
    tbl_data_list = []
    
    # Add header
    true_nof = len(dat_data_list)
    pad = 0
    true_nof_hex = true_nof.to_bytes(4, "little")
    pad_hex = pad.to_bytes(4, "little")
    tbl_data_list.append(true_nof_hex)
    tbl_data_list.append(pad_hex)
    # Rest of the data
    offset = 0 
    for file in dat_data_list:
        # TBL:
        size = len(file)
        tbl_data_list.append(offset.to_bytes(4, "little"))
        tbl_data_list.append(size.to_bytes(4, "little"))
        offset = offset + size



    return tbl_data_list

