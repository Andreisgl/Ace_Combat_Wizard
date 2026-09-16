import os
import sys

from PySide6.QtWidgets import QApplication, QDialog

import game_registry
from gui.main_window import MainWindow
from gui.project_picker_dialog import ProjectPickerDialog


def main():
    app = QApplication(sys.argv)

    projects_root = game_registry.default_projects_root()
    os.makedirs(projects_root, exist_ok=True)

    picker = ProjectPickerDialog(projects_root)
    if picker.exec() != QDialog.Accepted or picker.project is None:
        sys.exit(0)

    window = MainWindow(picker.project)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
