'''GIM-specific metadata: dimensions, color depth, channels, palette size.'''
from asset_classes import Asset, GIM
from metadata.base import MetadataProvider
from visualizers.gim_image import GimDecodeError, detect_gim_format


def _get_fields(asset: Asset) -> list[tuple[str, str]]:
    data = asset.get_raw_data()
    try:
        fmt = detect_gim_format(data)
    except GimDecodeError as exc:
        return [('Error', str(exc))]

    return [
        ('Width', f'{fmt.width}px'),
        ('Height', f'{fmt.height}px'),
        ('Color depth', f'{fmt.bits_per_pixel}-bit indexed'),
        ('Palette size', f'{fmt.palette_entries} colors'),
        ('Channels', 'RGBA (4)'),
        ('Pixel format', f'INDEX{fmt.bits_per_pixel}'),
        ('File size', f'{len(data):,} bytes'),
    ]


GIM_METADATA = MetadataProvider(
    id='gim',
    applies_to=lambda asset: isinstance(asset, GIM),
    get_fields=_get_fields,
)
