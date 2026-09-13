'''Mandatory "Raw Data" visualizer: a HxD-style hex dump, applicable to any asset.'''
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit

from asset_classes import Asset
from visualizers.base import Visualizer

MAX_PREVIEW_BYTES = 1024 * 1024  # 1 MiB - avoids freezing the UI on huge assets (e.g. the DATA.PAC root).


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


def _build_raw_data_widget(asset: Asset) -> QPlainTextEdit:
    data = asset.get_raw_data()
    truncated = len(data) > MAX_PREVIEW_BYTES
    preview = data[:MAX_PREVIEW_BYTES] if truncated else data

    text = format_hex_dump(preview)
    if truncated:
        text += f'\n\n... truncated, showing first {MAX_PREVIEW_BYTES:,} of {len(data):,} bytes'

    text_edit = QPlainTextEdit()
    text_edit.setReadOnly(True)
    text_edit.setFont(QFont('Consolas', 9))
    text_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
    text_edit.setPlainText(text)
    return text_edit


RAW_DATA = Visualizer(
    id='raw_data',
    label='Raw Data',
    applies_to=lambda asset: True,
    build_widget=_build_raw_data_widget,
)
