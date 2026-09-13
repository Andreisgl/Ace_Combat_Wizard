from PySide6.QtWidgets import QMainWindow, QTreeView

from asset_classes import ACZProject
from gui.asset_tree_model import AssetTreeModel


class MainWindow(QMainWindow):
    def __init__(self, project: ACZProject, parent=None):
        super().__init__(parent)
        self.project = project

        self.setWindowTitle(f'Ace Combat Wizard - {project.project_name}')
        self.resize(900, 600)

        self.model = AssetTreeModel(project.DATA_PAC)
        self.tree_view = QTreeView(self)
        self.tree_view.setModel(self.model)
        self.tree_view.setColumnWidth(0, 320)
        self.setCentralWidget(self.tree_view)
