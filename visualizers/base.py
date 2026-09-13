'''Base definition for a pluggable asset visualizer.'''
from dataclasses import dataclass
from typing import Callable

from PySide6.QtWidgets import QWidget

from asset_classes import Asset


@dataclass
class Visualizer:
    id: str
    label: str
    applies_to: Callable[[Asset], bool]
    build_widget: Callable[[Asset], QWidget]
