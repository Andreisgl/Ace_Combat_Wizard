'''DAT header visualizer: a readable view of a DatFile's already-parsed
header (header/offset_table/sizes_list), not a raw re-parse of its bytes.

Reusing those attributes (rather than independently decoding the header from
asset.get_raw_data()) keeps this in sync with whatever actually built the
asset tree - DatFile.init_offset_table() is load-bearing application logic,
not visualization-only decoding, so there must be exactly one implementation
of it. Reading them live (not caching a copy here) also means this stays
correct if a future repack feature recomputes them after an edit.'''
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit, QWidget

from asset_classes import Asset, DatFile
from visualizers.base import Visualizer


def format_dat_header(dat_file: DatFile) -> str:
    '''Formats dat_file.header (raw per-slot values, in original order, 0 =
    empty slot) as one readable row per slot, with the computed size
    (from sizes_list/offset_table) alongside each populated slot.'''
    if not dat_file.header:
        return 'No header data parsed for this asset.'

    number_of_files, slots = dat_file.header[0], dat_file.header[1:]
    size_by_offset = dict(zip(dat_file.offset_table, dat_file.sizes_list))

    lines = [
        f'dat_type: {dat_file.dat_type or "(unspecified)"}',
        f'slots: {number_of_files}',
        '',
        f'{"slot":>6}  {"raw offset":>12}  {"size":>10}',
    ]
    for i, value in enumerate(slots):
        if value == 0:
            lines.append(f'{i:>6}  {"(empty)":>12}')
        else:
            size = size_by_offset.get(value, '?')
            lines.append(f'{i:>6}  {value:>12}  {size:>10}')

    return '\n'.join(lines)


def _build_dat_header_widget(asset: Asset) -> QWidget:
    text_edit = QPlainTextEdit()
    text_edit.setReadOnly(True)
    text_edit.setFont(QFont('Consolas', 9))
    text_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
    text_edit.setPlainText(format_dat_header(asset))
    return text_edit


DAT_HEADER = Visualizer(
    id='dat_header',
    label='Header',
    applies_to=lambda asset: isinstance(asset, DatFile),
    build_widget=_build_dat_header_widget,
)
