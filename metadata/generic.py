'''Universal fallback metadata: basic Asset fields available regardless of content format.'''
from asset_classes import Asset
from metadata.base import MetadataProvider


def get_generic_fields(asset: Asset) -> list[tuple[str, str]]:
    '''Base fields common to any asset - reused by other providers (e.g.
    container_metadata.py) that want to extend rather than replace these.'''
    return [
        ('Name', asset.name),
        ('Type', type(asset).__name__),
        ('Size', f'{asset.size:,} bytes'),
        ('Offset', str(asset.offset_ref)),
    ]


GENERIC = MetadataProvider(
    id='generic',
    applies_to=lambda asset: True,
    get_fields=get_generic_fields,
)
