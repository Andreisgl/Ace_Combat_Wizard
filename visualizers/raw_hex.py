'''Mandatory "Raw Data" visualizer: a HxD-style hex dump, applicable to any asset.'''
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit

from asset_classes import Asset
from hex_format import MAX_PREVIEW_BYTES, format_hex_dump
from visualizers.base import Visualizer


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
