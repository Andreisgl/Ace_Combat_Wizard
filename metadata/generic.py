'''Universal fallback metadata: basic Asset fields available regardless of content format.'''
from asset_classes import Asset
from metadata.base import MetadataProvider


def _get_fields(asset: Asset) -> list[tuple[str, str]]:
    return [
        ('Name', asset.name),
        ('Type', type(asset).__name__),
        ('Size', f'{asset.size:,} bytes'),
        ('Offset', str(asset.offset_ref)),
    ]


GENERIC = MetadataProvider(
    id='generic',
    applies_to=lambda asset: True,
    get_fields=_get_fields,
)
