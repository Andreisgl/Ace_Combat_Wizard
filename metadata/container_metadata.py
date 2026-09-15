'''Container-type metadata: generic base fields plus child count.'''
from asset_classes import Container
from metadata.base import MetadataProvider
from metadata.generic import get_generic_fields


def _get_fields(asset: Container) -> list[tuple[str, str]]:
    return get_generic_fields(asset) + [
        ('Children', str(len(asset.children))),
    ]


CONTAINER_METADATA = MetadataProvider(
    id='container',
    applies_to=lambda asset: isinstance(asset, Container),
    get_fields=_get_fields,
)
