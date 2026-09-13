'''Registry of pluggable asset visualizers.

Each Visualizer takes an Asset and produces a widget. Kept separate from
asset_classes.py because content format (image/audio/3D/text/raw) is
orthogonal to the Asset/Container structural hierarchy, and per
PROGRAM_STRUCUTRE.MD these are meant to be independent modules, not
data-model methods.'''
from asset_classes import Asset
from visualizers.base import Visualizer
from visualizers.raw_hex import RAW_DATA

ALL_VISUALIZERS: list[Visualizer] = [
    RAW_DATA,
]


def get_available_visualizers(asset: Asset) -> list[Visualizer]:
    '''Returns every registered visualizer applicable to this asset.'''
    return [v for v in ALL_VISUALIZERS if v.applies_to(asset)]
