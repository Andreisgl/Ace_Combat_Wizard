'''Base definition for a pluggable per-asset-type metadata provider.'''
from dataclasses import dataclass
from typing import Callable

from asset_classes import Asset


@dataclass
class MetadataProvider:
    id: str
    applies_to: Callable[[Asset], bool]
    get_fields: Callable[[Asset], list[tuple[str, str]]]
