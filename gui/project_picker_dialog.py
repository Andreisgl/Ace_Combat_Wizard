'''Startup/File-menu "Open Project" dialog: lists valid project folders
found under a projects root, plus options to browse elsewhere or create a
new project.'''
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

import game_registry
from asset_classes import Project
from gui.new_project_dialog import NewProjectDialog


class ProjectPickerDialog(QDialog):
    def __init__(self, projects_root: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Open Project')
        self.resize(420, 320)

        self._projects_root = projects_root
        self.project: Project | None = None

        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._on_open_clicked)
        self._list.itemSelectionChanged.connect(self._update_open_enabled)
        self._populate_list()

        self._open_button = QPushButton('Open')
        self._open_button.setEnabled(False)
        self._open_button.clicked.connect(self._on_open_clicked)
        browse_button = QPushButton('Browse...')
        browse_button.clicked.connect(self._on_browse_clicked)
        new_button = QPushButton('New Project...')
        new_button.clicked.connect(self._on_new_project_clicked)

        button_row = QHBoxLayout()
        button_row.addWidget(self._open_button)
        button_row.addWidget(browse_button)
        button_row.addWidget(new_button)
        button_row.addStretch(1)

        box = QDialogButtonBox(QDialogButtonBox.Cancel)
        box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f'Projects in {projects_root}:'))
        layout.addWidget(self._list, 1)
        layout.addLayout(button_row)
        layout.addWidget(box)

    def _populate_list(self):
        self._list.clear()
        if not os.path.isdir(self._projects_root):
            return

        for entry in sorted(os.listdir(self._projects_root)):
            folder_path = os.path.join(self._projects_root, entry)
            if not os.path.isdir(folder_path):
                continue
            metadata = Project.read_acw_metadata(folder_path)
            if metadata is None:
                continue

            label = metadata.get('project_name', entry)
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, folder_path)
            self._list.addItem(item)

    def _update_open_enabled(self):
        self._open_button.setEnabled(bool(self._list.selectedItems()))

    def _on_open_clicked(self):
        items = self._list.selectedItems()
        if not items:
            return
        self._try_open(items[0].data(Qt.UserRole))

    def _on_browse_clicked(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Browse for Project Folder')
        if folder_path:
            self._try_open(folder_path)

    def _try_open(self, folder_path: str):
        try:
            self.project = game_registry.open_project(folder_path)
        except game_registry.ProjectIOError as exc:
            QMessageBox.critical(self, 'Open Project Failed', str(exc))
            return
        self.accept()

    def _on_new_project_clicked(self):
        dialog = NewProjectDialog(self._projects_root, self)
        if dialog.exec() == QDialog.Accepted and dialog.project is not None:
            self.project = dialog.project
            self.accept()
