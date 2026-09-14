'''GIM image visualizer.

Decodes the 128x128 INDEX8 GIM variant this game's TM2->GIM toolchain
produces. The byte layout was reverse-engineered from the actual
"[ACZ] ACE COMBAT TM2 to GIM converter.py" tool (by Death_the_d0g, already
credited as a contributor to this project in main.py), cross-checked against
real sample .GIM files - not from the generic "GIM" spec found online, which
turned out to describe an unrelated Sony PSP-era format.

Pixel indices are stored linear/row-major (confirmed by a real render
matching the expected image) - no pixel swizzle/deswizzle is needed for this
variant. The 256-entry palette, however, uses PS2 GS "CSM1" storage (confirmed
by the "CSM1 CLUT" option selected in this game's own TIM2 export dialog, per
the modding tutorial this format was reverse-engineered from), which stores
entries in an interleaved block order that needs undoing - see
_deinterleave_csm1_palette.'''
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QWidget

from asset_classes import Asset, GIM
from visualizers.base import Visualizer

GIM_SIGNATURE = b'GIM\x00'
HEADER_SIZE = 32  # through width/height fields
PADDING_AFTER_PIXELS = 12
PALETTE_MARKER = b'\x10\x00\x10\x00'  # 16, 0, 16, 0
PALETTE_ENTRIES = 256
PALETTE_SIZE = PALETTE_ENTRIES * 4
DISPLAY_SCALE = 4  # the source images are only 128x128; scale up so detail is checkable


def _rescale_ps2_alpha(value: int) -> int:
    '''PS2 GS hardware stores alpha as 7-bit (0x00-0x80 = fully transparent to
    fully opaque), not standard 8-bit (0x00-0xFF). Left unscaled, a fully-opaque
    0x80 reads as ~50% opaque, letting the background bleed through unevenly -
    this is what showed up as "noise" in the first render.'''
    return min(value * 2, 255)


def _deinterleave_csm1_palette(palette: bytes) -> bytes:
    '''PS2 GS "CSM1" 256-entry CLUTs are stored in blocks of 32 entries, with
    entries 8-15 and 16-23 of each block swapped relative to logical index
    order. This undoes that so palette[i] is the color for logical index i.'''
    entries = [palette[i * 4:i * 4 + 4] for i in range(PALETTE_ENTRIES)]
    reordered = entries[:]
    for block_start in range(0, PALETTE_ENTRIES, 32):
        for i in range(8):
            a, b = block_start + 8 + i, block_start + 16 + i
            reordered[a], reordered[b] = entries[b], entries[a]
    return b''.join(reordered)


class GimDecodeError(ValueError):
    '''Raised when raw bytes don't match the confirmed GIM INDEX8 128x128 layout.'''


def decode_gim(data: bytes) -> tuple[int, int, bytes]:
    '''Parses a GIM INDEX8 file and returns (width, height, rgba_bytes),
    where rgba_bytes is width*height*4 bytes, palette-resolved, RGBA8888,
    row-major as stored in the file.'''
    if len(data) < HEADER_SIZE:
        raise GimDecodeError(f'File too short for a GIM header ({len(data)} bytes)')

    if data[:4] != GIM_SIGNATURE:
        raise GimDecodeError(f"Bad signature: expected {GIM_SIGNATURE!r}, got {data[:4]!r}")

    width = int.from_bytes(data[28:30], byteorder='little')
    height = int.from_bytes(data[30:32], byteorder='little')
    if width <= 0 or height <= 0:
        raise GimDecodeError(f'Invalid dimensions: {width}x{height}')

    pixel_start = HEADER_SIZE
    pixel_end = pixel_start + width * height
    marker_start = pixel_end + PADDING_AFTER_PIXELS
    marker_end = marker_start + len(PALETTE_MARKER)
    palette_start = marker_end
    palette_end = palette_start + PALETTE_SIZE

    if palette_end != len(data):
        raise GimDecodeError(
            f'Size mismatch: header claims {width}x{height} '
            f'(expects a {palette_end}-byte file), actual size is {len(data)}'
        )

    marker = data[marker_start:marker_end]
    if marker != PALETTE_MARKER:
        raise GimDecodeError(f'Unexpected palette marker: expected {PALETTE_MARKER!r}, got {marker!r}')

    index_data = data[pixel_start:pixel_end]
    palette = bytearray(_deinterleave_csm1_palette(data[palette_start:palette_end]))
    for i in range(3, len(palette), 4):
        palette[i] = _rescale_ps2_alpha(palette[i])

    rgba = bytearray(len(index_data) * 4)
    for i, index in enumerate(index_data):
        rgba[i * 4:i * 4 + 4] = palette[index * 4:index * 4 + 4]

    return width, height, bytes(rgba)


def _build_gim_widget(asset: Asset) -> QWidget:
    data = asset.get_raw_data()
    try:
        width, height, rgba = decode_gim(data)
    except GimDecodeError as exc:
        return QLabel(f"Can't display this GIM image:\n{exc}")

    image = QImage(rgba, width, height, width * 4, QImage.Format_RGBA8888).copy()
    pixmap = QPixmap.fromImage(image)
    # FastTransformation (nearest-neighbor) keeps pixel edges crisp instead of
    # blurring them, so individual pixels stay inspectable at the larger size.
    pixmap = pixmap.scaled(width * DISPLAY_SCALE, height * DISPLAY_SCALE, Qt.KeepAspectRatio, Qt.FastTransformation)

    label = QLabel()
    label.setPixmap(pixmap)
    return label


GIM_IMAGE = Visualizer(
    id='gim_image',
    label='Image',
    applies_to=lambda asset: isinstance(asset, GIM),
    build_widget=_build_gim_widget,
)
