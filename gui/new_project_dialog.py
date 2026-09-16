'''"New Project" dialog: collects a name and a game, then prompts for that
game's required source files and creates the project via game_registry.'''
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

import game_registry
from asset_classes import Project


class NewProjectDialog(QDialog):
    def __init__(self, projects_root: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle('New Project')

        self._projects_root = projects_root
        self.project: Project | None = None

        self._name_edit = QLineEdit()
        self._game_combo = QComboBox()
        for game_id, display_name in game_registry.list_games():
            self._game_combo.addItem(display_name, userData=game_id)

        form = QFormLayout()
        form.addRow('Project name:', self._name_edit)
        form.addRow('Game:', self._game_combo)

        box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        box.button(QDialogButtonBox.Ok).setText('Create...')
        box.accepted.connect(self._on_create)
        box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(box)

    def _on_create(self):
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, 'New Project', 'Enter a project name.')
            return

        game_id = self._game_combo.currentData()
        project_class = game_registry.GAME_REGISTRY[game_id]

        required = ', '.join(project_class.REQUIRED_SOURCE_FILES)
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, f'Select {project_class.DISPLAY_NAME} game files ({required})')
        if not file_paths:
            return

        try:
            self.project = game_registry.create_project(self._projects_root, name, game_id, file_paths)
        except game_registry.ProjectIOError as exc:
            QMessageBox.critical(self, 'New Project Failed', str(exc))
            return

        self.accept()
