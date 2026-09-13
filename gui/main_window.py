from PySide6.QtWidgets import QAbstractItemView, QMainWindow, QSplitter, QTreeView

from asset_classes import ACZProject, Asset
from gui.asset_panel import AssetPanel
from gui.asset_tree_model import AssetTreeModel


class MainWindow(QMainWindow):
    def __init__(self, project: ACZProject, parent=None):
        super().__init__(parent)
        self.project = project

        self.setWindowTitle(f'Ace Combat Wizard - {project.project_name}')
        self.resize(1200, 700)

        self.model = AssetTreeModel(project.DATA_PAC)
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setColumnWidth(0, 320)
        self.tree_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tree_view.selectionModel().selectionChanged.connect(self._on_selection_changed)

        self.asset_panel = AssetPanel()

        splitter = QSplitter()
        splitter.addWidget(self.tree_view)
        splitter.addWidget(self.asset_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

    def _on_selection_changed(self):
        indexes = self.tree_view.selectionModel().selectedIndexes()
        asset: Asset | None = indexes[0].internalPointer() if indexes else None
        self.asset_panel.set_asset(asset)
