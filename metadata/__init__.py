'''Registry of pluggable per-asset-type metadata providers.

Mirrors visualizers/__init__.py's design: list order is priority, first
applicable provider wins. GENERIC (applies to everything) is listed last so
type-specific providers take priority wherever they apply.'''
from asset_classes import Asset
from metadata.base import MetadataProvider
from metadata.generic import GENERIC
from metadata.gim_metadata import GIM_METADATA

ALL_METADATA_PROVIDERS: list[MetadataProvider] = [
    GIM_METADATA,
    GENERIC,
]


def get_metadata_fields(asset: Asset) -> list[tuple[str, str]]:
    '''Returns the (label, value) fields from the first applicable provider.'''
    for provider in ALL_METADATA_PROVIDERS:
        if provider.applies_to(asset):
            return provider.get_fields(asset)
    return []
