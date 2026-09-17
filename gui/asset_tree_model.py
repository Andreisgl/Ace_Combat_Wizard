'''Qt tree model that renders the Asset/Container object graph from asset_classes.py directly.

Holds no copy of the asset data - each QModelIndex's internalPointer() is the
live Asset object itself, so future features (thumbnails, diff-state) can be
read straight off those same objects without keeping a parallel tree in sync.'''
from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt

from asset_classes import Asset, Container

COLUMNS = ('Name', 'Type', 'Size', 'Offset')


class AssetTreeModel(QAbstractItemModel):
    def __init__(self, root_asset: Container, parent=None):
        super().__init__(parent)
        self._root = root_asset

    def index(self, row, column, parent=QModelIndex()):
        if not parent.isValid():
            if row == 0:
                return self.createIndex(row, column, self._root)
            return QModelIndex()

        parent_asset = parent.internalPointer()
        if not isinstance(parent_asset, Container):
            return QModelIndex()

        # Positional (insertion-order) lookup, not a dict-key lookup: children
        # dicts aren't always keyed 0..N-1 contiguously - e.g. DatFile skips
        # empty header slots, so keys can have gaps (0, 2, 3, ...).
        siblings = list(parent_asset.children.values())
        if row < 0 or row >= len(siblings):
            return QModelIndex()
        return self.createIndex(row, column, siblings[row])

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        asset = index.internalPointer()
        if asset is self._root:
            return QModelIndex()

        parent_asset = asset.father
        if parent_asset is self._root:
            return self.createIndex(0, 0, self._root)
        return self.createIndex(self._row_of(parent_asset), 0, parent_asset)

    def _row_of(self, asset) -> int:
        '''Positional row of `asset` among its father's children (insertion
        order) - see the note in index() about why this isn't index_father.'''
        father = asset.father
        if not isinstance(father, Container):
            return 0
        siblings = list(father.children.values())
        return siblings.index(asset) if asset in siblings else 0

    def index_for(self, asset) -> QModelIndex:
        '''Builds a QModelIndex for `asset` as it currently sits in the tree.
        Used to retarget persistent indexes (the tree view's expanded-state
        and selection bookkeeping) when a child object is swapped for a
        different one at the same position - e.g. Asset.cast_to - via
        layoutChanged + changePersistentIndex, instead of a full model
        reset that would collapse the whole tree.'''
        if asset is self._root:
            return self.createIndex(0, 0, self._root)
        return self.createIndex(self._row_of(asset), 0, asset)

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return 1

        asset = parent.internalPointer()
        if not isinstance(asset, Container):
            return 0
        return len(asset.children)

    def columnCount(self, parent=QModelIndex()):
        return len(COLUMNS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        asset: Asset = index.internalPointer()
        column = index.column()
        if column == 0:
            return asset.name
        if column == 1:
            return asset.display_type
        if column == 2:
            return str(asset.size)
        if column == 3:
            return str(getattr(asset, 'offset_ref', ''))
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return COLUMNS[section]
        return None
