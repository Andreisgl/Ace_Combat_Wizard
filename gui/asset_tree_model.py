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
        self._fetched_ids: set[int] = set()

    def index(self, row, column, parent=QModelIndex()):
        if not parent.isValid():
            if row == 0:
                return self.createIndex(row, column, self._root)
            return QModelIndex()

        parent_asset = parent.internalPointer()
        if not isinstance(parent_asset, Container):
            return QModelIndex()

        child = parent_asset.children.get(row)
        if child is None:
            return QModelIndex()
        return self.createIndex(row, column, child)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        asset = index.internalPointer()
        if asset is self._root:
            return QModelIndex()

        parent_asset = asset.father
        if parent_asset is self._root:
            return self.createIndex(0, 0, self._root)
        return self.createIndex(parent_asset.index_father, 0, parent_asset)

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return 1

        asset = parent.internalPointer()
        if not isinstance(asset, Container):
            return 0
        return len(asset.children)

    def columnCount(self, parent=QModelIndex()):
        return len(COLUMNS)

    def hasChildren(self, parent=QModelIndex()):
        if not parent.isValid():
            return True

        asset = parent.internalPointer()
        if not isinstance(asset, Container):
            return False
        if asset.children:
            return True
        return id(asset) not in self._fetched_ids

    def canFetchMore(self, parent):
        if not parent.isValid():
            return False

        asset = parent.internalPointer()
        if not isinstance(asset, Container):
            return False
        return not asset.children and id(asset) not in self._fetched_ids

    def fetchMore(self, parent):
        asset = parent.internalPointer()
        asset.init_offset_table()

        count = len(asset.offset_table)
        if count > 0:
            self.beginInsertRows(parent, 0, count - 1)
        asset.generate_children()
        self._fetched_ids.add(id(asset))
        if count > 0:
            self.endInsertRows()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        asset: Asset = index.internalPointer()
        column = index.column()
        if column == 0:
            return asset.name
        if column == 1:
            return type(asset).__name__
        if column == 2:
            return str(asset.size)
        if column == 3:
            return str(getattr(asset, 'offset_ref', ''))
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return COLUMNS[section]
        return None
