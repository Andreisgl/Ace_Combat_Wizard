# This module is responsible for extracting and rebuilding .PAC files.
# Code based on the "ACZ_PAC_TOOLS.2" by Death_the_d0g (deaththed0g @ Github, Death_the_d0g @ Twitter)

import argparse
import os
import sys

# --- UNPACKING LOGIC ---
def unpack_pac(pac_path, tbl_path, output_path, names_file=None):
    """
    Extracts the contents of a .PAC file using a corresponding .TBL file.

    :param pac_path: Path to the input DATA.PAC file.
    :param tbl_path: Path to the input DATA.TBL file.
    :param output_path: Directory where the extracted files will be saved.
    :param names_file: (Optional) Path to a text file with the names for the output files.
    """
    print(f"UNPACK mode activated.")
    print(f"  -> Input PAC: {pac_path}")
    print(f"  -> Input TBL: {tbl_path}")
    print(f"  -> Output directory: {output_path}")

    if not os.path.isfile(pac_path):
        print(f"Error: PAC file '{pac_path}' not found.")
        sys.exit(1)
    if not os.path.isfile(tbl_path):
        print(f"Error: TBL file '{tbl_path}' not found.")
        sys.exit(1)
    
    os.makedirs(output_path, exist_ok=True)

    file_names = []
    if names_file:
        if not os.path.isfile(names_file):
            print(f"Warning: Names file '{names_file}' not found. Using default numeric names.")
        else:
            print(f"  -> Using name map: {names_file}")
            with open(names_file, 'r', encoding='utf-8') as f:
                file_names = f.read().splitlines()
            print(f"  -> {len(file_names)} lines loaded from name map.")

    # Reading the TBL
    offset_list = []
    size_list = []
    with open(tbl_path, 'rb') as tbl_file:
        tbl_nof = int.from_bytes(tbl_file.read(4), byteorder="little")
        tbl_file.seek(8)
        for _ in range(tbl_nof):
            offset_list.append(int.from_bytes(tbl_file.read(4), byteorder="little"))
            size_list.append(int.from_bytes(tbl_file.read(4), byteorder="little"))

    # Determines the amount of zero-padding needed for file prefixes.
    padding_width = len(str(tbl_nof - 1)) if tbl_nof > 0 else 1
    print(f"Info: Total files: {tbl_nof}. Using a zero-padding of {padding_width} for prefixes.")

    # Extracting from the PAC
    with open(pac_path, 'rb') as pac_file:
        for i in range(tbl_nof):
            base_name = ""
            
            if i < len(file_names):
                potential_name = file_names[i].strip()
                if potential_name:
                    base_name = potential_name
            
            if not base_name:
                # .dat only, as the prefix is already added by default.
                base_name = ".dat"
            
            # Assemble final name with prefix
            prefix = f"{i:0{padding_width}d}"
            
            # Join prefix and base name. Add '_' if name is not an extension.
            separator = "_" if not base_name.startswith('.') else ''
            final_name = f"{prefix}{separator}{base_name}"

            offset = offset_list[i]
            size = size_list[i]
            
            pac_file.seek(offset)
            data = pac_file.read(size)
            
            output_file_path = os.path.join(output_path, final_name)
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            with open(output_file_path, 'wb') as f_out:
                f_out.write(data)

            print(f"File (Index {i}): {final_name}, Offset: {hex(offset)}, Size: {size}")

    print("\nExtraction completed successfully!")

# --- REPACKING LOGIC ---
def repack_pac(input_path, output_path):
    print(f"REPACK mode activated.")
    print(f"  -> Input directory: {input_path}")
    print(f"  -> Output PAC: {output_path}")

    if not os.path.isdir(input_path):
        print(f"Error: Input directory '{input_path}' not found.")
        sys.exit(1)

    data_list = []
    
    file_names = sorted(os.listdir(input_path))
    
    for file_name in file_names:
        file_path = os.path.join(input_path, file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
                data_list.append(data)
                print(f"Adding file: {file_name}, Size: {len(data)}")
    
    out_pac_data, out_tbl_data = assemble_pac(data_list)
    
    with open(output_path, 'wb') as fpac:
        fpac.write(out_pac_data)
    
    tbl_path = os.path.splitext(output_path)[0] + '.TBL'
    with open(tbl_path, 'wb') as ftbl:
        ftbl.write(out_tbl_data)
    
    print(f"\nRepack completed! Files generated:\n  -> {output_path}\n  -> {tbl_path}")

def assemble_pac(dat_data_list):
    print("\nBuilding DATA.TBL...")
    tbl_entries = []
    offset = 0
    for file_data in dat_data_list:
        size = len(file_data)
        tbl_entries.append(offset.to_bytes(4, "little"))
        tbl_entries.append(size.to_bytes(4, "little"))
        offset += size
    
    header = len(dat_data_list).to_bytes(4, "little") + (0).to_bytes(4, "little")
    final_tbl_data = header + b''.join(tbl_entries)

    print("Building DATA.PAC...")
    final_pac_data = b''.join(dat_data_list)

    return final_pac_data, final_tbl_data

# --- ENTRY POINT AND ARGUMENT PARSER ---
def main():
    parser = argparse.ArgumentParser(
        description="A tool to extract and rebuild Ace Combat Zero PAC files.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='mode', required=True, help='Operating mode')

    parser_unpack = subparsers.add_parser('unpack', help='Extract a .PAC file.')
    parser_unpack.add_argument('input_pac', help='Path to the input .PAC file (e.g., DATA.PAC).')
    parser_unpack.add_argument('output_dir', help='Output directory for the extracted files.')
    parser_unpack.add_argument('--names', dest='names_file', default=None,
                               help='(Optional) Path to the .csv/.txt file with the list of names for the output files.')

    parser_repack = subparsers.add_parser('repack', help='Rebuild a .PAC file from a directory.')
    parser_repack.add_argument('input_dir', help='Input directory containing the files.')
    parser_repack.add_argument('output_pac', help='Path for the output .PAC file (e.g., DATA_MOD.PAC).')

    args = parser.parse_args()

    if args.mode == 'unpack':
        tbl_path = os.path.splitext(args.input_pac)[0] + '.TBL'
        unpack_pac(args.input_pac, tbl_path, args.output_dir, args.names_file)
    elif args.mode == 'repack':
        repack_pac(args.input_dir, args.output_pac)

if __name__ == '__main__':
    main()
