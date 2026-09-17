'''Pure hex-dump formatting - no GUI dependency, so both the GUI's Raw Data
visualizer (visualizers/raw_hex.py) and the Qt-free CLI (cli.py) can share
one implementation without either pulling in the other's dependencies.'''

MAX_PREVIEW_BYTES = 1024 * 1024  # 1 MiB - avoids freezing on huge assets (e.g. DATA.PAC itself).


def format_hex_dump(data: bytes, bytes_per_row: int = 16) -> str:
    '''Formats bytes as "offset | hex bytes | ascii" rows, like HxD.'''
    lines = []
    for row_start in range(0, len(data), bytes_per_row):
        row = data[row_start:row_start + bytes_per_row]
        hex_part = ' '.join(f'{b:02x}' for b in row)
        hex_part = hex_part.ljust(bytes_per_row * 3 - 1)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in row)
        lines.append(f'{row_start:08x}  {hex_part}  {ascii_part}')
    return '\n'.join(lines)
