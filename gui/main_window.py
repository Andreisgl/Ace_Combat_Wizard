from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QTreeView,
)

import game_registry
from asset_classes import Asset, Project
from gui.asset_panel import AssetPanel
from gui.asset_tree_model import AssetTreeModel
from gui.project_picker_dialog import ProjectPickerDialog


class MainWindow(QMainWindow):
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.resize(1200, 700)
        self._build_menu_bar()

        self.tree_view = QTreeView()
        self.tree_view.setColumnWidth(0, 320)
        self.tree_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree_view.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.asset_panel = AssetPanel()

        splitter = QSplitter()
        splitter.addWidget(self.tree_view)
        splitter.addWidget(self.asset_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        self.load_project(project)

    def load_project(self, project: Project):
        '''Swaps in `project` as the active project - used both for the
        initial load and for later File > Open Project/Save As actions, so
        there's exactly one place that wires a project into the tree/panel.'''
        self.project = project
        self.setWindowTitle(f'Ace Combat Wizard - {project.project_name}')

        self.model = AssetTreeModel(project.DATA_PAC)
        self.tree_view.setModel(self.model)
        # setModel() creates a new selection model each call, so this
        # connection must be redone on every load, not just once in __init__.
        self.tree_view.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.asset_panel.set_asset(None)

    def _build_menu_bar(self):
        file_menu = self.menuBar().addMenu('&File')

        open_action = file_menu.addAction('Open Project...')
        open_action.triggered.connect(self._on_open_project)

        save_action = file_menu.addAction('Save')
        save_action.setEnabled(False)  # No write-back/dirty state to persist yet.

        save_as_action = file_menu.addAction('Save As...')
        save_as_action.triggered.connect(self._on_save_as)

    def _on_open_project(self):
        dialog = ProjectPickerDialog(game_registry.default_projects_root(), self)
        if dialog.exec() == QDialog.Accepted and dialog.project is not None:
            self.load_project(dialog.project)

    def _on_save_as(self):
        new_name, ok = QInputDialog.getText(self, 'Save As', 'New project name:')
        if not ok or not new_name.strip():
            return

        try:
            new_project = game_registry.duplicate_project(
                self.project, new_name.strip(), game_registry.default_projects_root())
        except game_registry.ProjectIOError as exc:
            QMessageBox.critical(self, 'Save As Failed', str(exc))
            return

        self.load_project(new_project)

    def _on_selection_changed(self):
        indexes = self.tree_view.selectionModel().selectedIndexes()
        asset: Asset | None = indexes[0].internalPointer() if indexes else None
        self.asset_panel.set_asset(asset)
