'''GIM image visualizer.

Decodes the GIM variants this game uses: INDEX8 (256-color palette, 1
byte/pixel) and INDEX4 (16-color palette, 2 pixels packed per byte). The
byte layout was reverse-engineered from the actual
"[ACZ] ACE COMBAT TM2 to GIM converter.py" tool (by Death_the_d0g, already
credited as a contributor to this project in main.py), cross-checked against
real sample .GIM files - not from the generic "GIM" spec found online, which
turned out to describe an unrelated Sony PSP-era format. That converter tool
only ever produces INDEX8 (it's for injecting custom textures); INDEX4 shows
up in the original game's own assets, which weren't made by that tool.

Pixel indices are stored linear/row-major (confirmed by a real render
matching the expected image) - no pixel swizzle/deswizzle is needed for
either variant.

The 4 bytes between the pixel data's trailing zero padding and the palette
were originally assumed to be a fixed magic marker (`10 00 10 00`, matching
every INDEX8 sample seen) - but a real INDEX4 sample has different bytes
there (`08 00 02 00`), proving it's real (if not yet understood) data, not a
constant. Its meaning is unconfirmed; only its fixed 4-byte length/position
is relied on here.

The 256-entry (INDEX8) palette uses PS2 GS "CSM1" storage (confirmed by the
"CSM1 CLUT" option selected in this game's own TIM2 export dialog, per the
modding tutorial this format was reverse-engineered from), which stores
entries in an interleaved block order that needs undoing - see
_deinterleave_csm1_palette. The 16-entry (INDEX4) palette is small enough
that PS2 GS doesn't apply that interleaving, so it's used as-is.

INDEX4 packs two pixel indices per byte; which nibble is the "first"
(leftmost) pixel isn't confirmed from any reference - low-nibble-first is
assumed below as the more common convention. If an INDEX4 image renders
with pixels swapped in pairs, that assumption is what to flip.'''
from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QWidget

from asset_classes import Asset, GIM
from visualizers.base import Visualizer

GIM_SIGNATURE = b'GIM\x00'
HEADER_SIZE = 32  # through width/height fields
PADDING_AFTER_PIXELS = 12
UNKNOWN_FIELD_SIZE = 4  # position/length only - see module docstring


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
    entries = [palette[i * 4:i * 4 + 4] for i in range(256)]
    reordered = entries[:]
    for block_start in range(0, 256, 32):
        for i in range(8):
            a, b = block_start + 8 + i, block_start + 16 + i
            reordered[a], reordered[b] = entries[b], entries[a]
    return b''.join(reordered)


def _unpack_nibbles(packed: bytes, pixel_count: int) -> bytes:
    '''Unpacks 2 pixel indices per byte (low nibble = first pixel) into 1 byte/pixel.'''
    unpacked = bytearray(pixel_count)
    for i, byte in enumerate(packed):
        unpacked[i * 2] = byte & 0x0F
        if i * 2 + 1 < pixel_count:
            unpacked[i * 2 + 1] = byte >> 4
    return bytes(unpacked)


class GimDecodeError(ValueError):
    '''Raised when raw bytes don't match a known GIM INDEX8/INDEX4 layout.'''


# (palette_entries, packed_2_pixels_per_byte)
_KNOWN_FORMATS = ((256, False), (16, True))


@dataclass
class GimFormat:
    '''Header-derived layout of a GIM file, without its pixel/palette bytes -
    cheap to compute, so metadata display doesn't need a full pixel decode.'''
    width: int
    height: int
    palette_entries: int
    packed: bool  # True = INDEX4 (2 pixels/byte), False = INDEX8 (1 pixel/byte)

    @property
    def bits_per_pixel(self) -> int:
        return 4 if self.packed else 8

    @property
    def pixel_start(self) -> int:
        return HEADER_SIZE

    @property
    def pixel_end(self) -> int:
        pixel_count = self.width * self.height
        packed_size = (pixel_count + 1) // 2 if self.packed else pixel_count
        return self.pixel_start + packed_size

    @property
    def palette_start(self) -> int:
        return self.pixel_end + PADDING_AFTER_PIXELS + UNKNOWN_FIELD_SIZE

    @property
    def palette_end(self) -> int:
        return self.palette_start + self.palette_entries * 4


def detect_gim_format(data: bytes) -> GimFormat:
    '''Parses just the header and determines which known layout (INDEX8 or
    INDEX4) the file matches, by exact total-size arithmetic.'''
    if len(data) < HEADER_SIZE:
        raise GimDecodeError(f'File too short for a GIM header ({len(data)} bytes)')

    if data[:4] != GIM_SIGNATURE:
        raise GimDecodeError(f"Bad signature: expected {GIM_SIGNATURE!r}, got {data[:4]!r}")

    width = int.from_bytes(data[28:30], byteorder='little')
    height = int.from_bytes(data[30:32], byteorder='little')
    if width <= 0 or height <= 0:
        raise GimDecodeError(f'Invalid dimensions: {width}x{height}')

    for palette_entries, packed in _KNOWN_FORMATS:
        fmt = GimFormat(width, height, palette_entries, packed)
        if fmt.palette_end == len(data):
            return fmt

    raise GimDecodeError(
        f'Size mismatch: header claims {width}x{height}, but that matches neither a known '
        f'INDEX8 nor INDEX4 layout for the actual file size {len(data)}'
    )


def decode_gim(data: bytes) -> tuple[int, int, bytes]:
    '''Parses a GIM INDEX8 or INDEX4 file and returns (width, height, rgba_bytes),
    where rgba_bytes is width*height*4 bytes, palette-resolved, RGBA8888,
    row-major as stored in the file.'''
    fmt = detect_gim_format(data)

    packed_index_data = data[fmt.pixel_start:fmt.pixel_end]
    index_data = _unpack_nibbles(packed_index_data, fmt.width * fmt.height) if fmt.packed else packed_index_data

    palette = bytearray(data[fmt.palette_start:fmt.palette_end])
    if fmt.palette_entries == 256:
        palette = bytearray(_deinterleave_csm1_palette(bytes(palette)))
    for i in range(3, len(palette), 4):
        palette[i] = _rescale_ps2_alpha(palette[i])

    rgba = bytearray(len(index_data) * 4)
    for i, index in enumerate(index_data):
        rgba[i * 4:i * 4 + 4] = palette[index * 4:index * 4 + 4]

    return fmt.width, fmt.height, bytes(rgba)


class _ImageLabel(QLabel):
    '''A QLabel that keeps its pixmap scaled to fit the label's current size,
    preserving aspect ratio (so it never crops) and using nearest-neighbor
    scaling so pixel edges stay crisp instead of blurring.'''

    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self._source_pixmap = pixmap
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(1, 1)  # allow shrinking below the image's own size
        self.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._source_pixmap.isNull():
            return
        scaled = self._source_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.setPixmap(scaled)


def _build_gim_widget(asset: Asset) -> QWidget:
    data = asset.get_raw_data()
    try:
        width, height, rgba = decode_gim(data)
    except GimDecodeError as exc:
        return QLabel(f"Can't display this GIM image:\n{exc}")

    image = QImage(rgba, width, height, width * 4, QImage.Format_RGBA8888).copy()
    return _ImageLabel(QPixmap.fromImage(image))


GIM_IMAGE = Visualizer(
    id='gim_image',
    label='Image',
    applies_to=lambda asset: isinstance(asset, GIM),
    build_widget=_build_gim_widget,
)
