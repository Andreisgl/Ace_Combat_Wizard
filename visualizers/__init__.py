'''Registry of pluggable asset visualizers.

Each Visualizer takes an Asset and produces a widget. Kept separate from
asset_classes.py because content format (image/audio/3D/text/raw) is
orthogonal to the Asset/Container structural hierarchy, and per
PROGRAM_STRUCUTRE.MD these are meant to be independent modules, not
data-model methods.

List order doubles as "auto mode" priority: get_available_visualizers()
preserves this order, and the GUI's "auto" mode picks the first applicable
entry as the default for that asset's type. Type-specific visualizers are
listed before RAW_DATA so they win as the default wherever they apply, while
RAW_DATA (applicable to everything) is the universal fallback.'''
from asset_classes import Asset
from visualizers.base import Visualizer
from visualizers.dat_header import DAT_HEADER
from visualizers.gim_image import GIM_IMAGE
from visualizers.raw_hex import RAW_DATA

ALL_VISUALIZERS: list[Visualizer] = [
    GIM_IMAGE,
    DAT_HEADER,
    RAW_DATA,
]


def get_available_visualizers(asset: Asset) -> list[Visualizer]:
    '''Returns every registered visualizer applicable to this asset.'''
    return [v for v in ALL_VISUALIZERS if v.applies_to(asset)]
