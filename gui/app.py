import os
import sys

from PySide6.QtWidgets import QApplication

from asset_classes import ACZProject
from gui.main_window import MainWindow


def build_test_project() -> ACZProject:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    projects_folder = os.path.join(repo_root, 'projects')
    project_path = os.path.join(projects_folder, 'testproj')
    return ACZProject(project_folder_path=project_path, name='test_proj')


def main():
    app = QApplication(sys.argv)
    project = build_test_project()
    window = MainWindow(project)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
