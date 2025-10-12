# This is a rewrite of the DAT unpacker
import os
import argparse
import sys

def line_fill(position, line_length):
    '''This function returns the ammount of characters/bytes
    necessary to fill up the rest of the current line.'''
    aux = position % line_length
    return (line_length - aux) % line_length

def unpack_dat(input_file, output_folder, names_file=None):
    '''Orchestrates the extraction of a .DAT file, reading its data,
    saving the sub-files with proper names, and creating a _zof.zof file.'''

    print(f"Unpacking {input_file}...")

    file_data_list = []
    zero_offset_list = []

    try:
        with open(input_file, 'rb') as file:
            # Read the raw data and null offset list from the .DAT
            read = file.read(4)
            if not read:
                print(f"Error: Input file '{input_file}' is empty.")
                sys.exit(1)
            
            number_of_files = int.from_bytes(read, byteorder="little")
            
            offset_list = []
            for offset_index in range(number_of_files):
                data = file.read(4)
                data_int = int.from_bytes(data, byteorder="little")
                if data_int != 0:
                    offset_list.append(data_int)
                else:
                    zero_offset_list.append(offset_index)

            # Read sub-file data
            # Add the total file size as the final offset to calculate the last sub-file's size
            file.seek(0, os.SEEK_END)
            offset_list.append(file.tell())

            for i in range(len(offset_list) - 1):
                start_offset = offset_list[i]
                end_offset = offset_list[i+1]
                size = end_offset - start_offset
                file.seek(start_offset)
                data = file.read(size)
                file_data_list.append(data)

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during file reading: {e}")
        sys.exit(1)

    # Save the extracted data and the _zof.zof file
    print(f"Found {len(file_data_list)} sub-files and {len(zero_offset_list)} zero-offset entries.")
    
    custom_names = []
    if names_file:
        if os.path.isfile(names_file):
            with open(names_file, 'r', encoding='utf-8') as f:
                custom_names = f.read().splitlines()
        else:
            print(f"Warning: Names file '{names_file}' not found. Using default names.")

    os.makedirs(output_folder, exist_ok=True)

    total_subfiles = len(file_data_list)
    padding_width = len(str(total_subfiles - 1)) if total_subfiles > 0 else 1

    for i, file_data in enumerate(file_data_list):
        base_name = ""
        
        if i < len(custom_names):
            potential_name = custom_names[i].strip()
            if potential_name:
                base_name = potential_name
        
        if not base_name:
            ext_bytes = file_data[:3]
            try:
                if ext_bytes.isalnum():
                    base_name = f".{ext_bytes.decode('ascii')}"
                else:
                    base_name = ".unk"
            except UnicodeDecodeError:
                base_name = ".unk"

        prefix = f"{i:0{padding_width}d}"
        separator = "_" if not base_name.startswith('.') else ''
        final_name = f"{prefix}{separator}{base_name}"
        
        file_path = os.path.join(output_folder, final_name)
        print(f"  -> Saving file (Index {i}): {final_name}")
        with open(file_path, 'wb') as f:
            f.write(file_data)

    zof_file_path = os.path.join(output_folder, '_zof.zof')
    with open(zof_file_path, 'w') as zof_file:
        zof_file.write('\n'.join(map(str, zero_offset_list)))
    print(f"  -> Zero Offset File saved to: {zof_file_path}")
    
    print("\nUnpack completed successfully!")

def repack_dat(in_folder, out_file):
    '''Rebuilds a .DAT file from a directory of sub-files and a _zof.zof file.'''
    print(f"Repacking {in_folder}...")
    
    zof_file_path = os.path.join(in_folder, '_zof.zof')
    if not os.path.isfile(zof_file_path):
        print(f"Error: _zof.zof file not found in '{in_folder}'!")
        sys.exit(1)

    with open(zof_file_path, 'r') as zof:
        content = zof.read().strip()
        zero_offset_list = [int(x) for x in content.splitlines() if x.strip()] if content else []

    subdat_paths = sorted([
        os.path.join(in_folder, f)
        for f in os.listdir(in_folder)
        if not f.endswith('.zof') and os.path.isfile(os.path.join(in_folder, f))
    ])

    header_contents = []
    offset_acc = 0
    for subdat_path in subdat_paths:
        header_contents.append(offset_acc)
        size = os.path.getsize(subdat_path)
        offset_acc += size
    
    total_header_entries = len(header_contents) + len(zero_offset_list)
    header_length = total_header_entries * 4
    header_length += line_fill(header_length, 16)

    header_contents = [x + header_length for x in header_contents]

    for zo in zero_offset_list:
        header_contents.insert(zo, 0)
        
    header_contents.insert(0, total_header_entries)

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'wb') as out_dat:
        for pos in header_contents:
            out_dat.write(pos.to_bytes(4, "little"))
        
        for file_path in subdat_paths:
            with open(file_path, 'rb') as subdat:
                out_dat.write(subdat.read())
    
    print(f"\nRepack completed successfully! Output: {out_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Tool to extract and rebuild Ace Combat Zero .DAT files.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='mode', required=True, help='Operating mode')

    parser_unpack = subparsers.add_parser('unpack', help='Extract a .DAT file.')
    parser_unpack.add_argument('input_dat', help='Path to the input .DAT file.')
    parser_unpack.add_argument('output_dir', help='Output directory for the extracted sub-files.')
    parser_unpack.add_argument('--names', dest='names_file', default=None,
                               help='(Optional) Path to a text file with the list of names for the output files.')

    parser_repack = subparsers.add_parser('repack', help='Rebuild a .DAT file from a directory.')
    parser_repack.add_argument('input_dir', help='Input directory containing the sub-files (and _zof.zof).')
    parser_repack.add_argument('output_dat', help='Path for the output .DAT file.')

    args = parser.parse_args()

    if args.mode == 'unpack':
        unpack_dat(args.input_dat, args.output_dir, args.names_file)
    elif args.mode == 'repack':
        repack_dat(args.input_dir, args.output_dat)

if __name__ == '__main__':
    main()
