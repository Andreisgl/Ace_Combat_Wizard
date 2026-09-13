from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from asset_classes import Asset
from visualizers import get_available_visualizers


class AssetPanel(QWidget):
    '''Right-hand panel: project/export actions, and a pluggable visualization
    area for whichever asset is currently selected in the tree.'''

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_asset: Asset | None = None
        self._visualizers = []
        self._viz_widget: QWidget | None = None

        self.open_project_button = QPushButton('Open Project')
        # Not wired to a handler yet - project picking isn't implemented.

        self.export_button = QPushButton('Export Asset')
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._on_export_clicked)

        button_row = QHBoxLayout()
        button_row.addWidget(self.open_project_button)
        button_row.addWidget(self.export_button)

        self.visualizer_combo = QComboBox()
        self.visualizer_combo.currentIndexChanged.connect(self._render_current)

        self._viz_container = QVBoxLayout()

        layout = QVBoxLayout(self)
        layout.addLayout(button_row)
        layout.addWidget(self.visualizer_combo)
        layout.addLayout(self._viz_container)

        self._show_placeholder('No asset selected')

    def set_asset(self, asset: Asset | None):
        self._current_asset = asset
        self.export_button.setEnabled(asset is not None)

        self.visualizer_combo.blockSignals(True)
        self.visualizer_combo.clear()
        if asset is not None:
            self._visualizers = get_available_visualizers(asset)
            self.visualizer_combo.addItems([v.label for v in self._visualizers])
        else:
            self._visualizers = []
        self.visualizer_combo.blockSignals(False)

        if asset is None:
            self._show_placeholder('No asset selected')
        else:
            self._render_current()

    def _render_current(self):
        if self._current_asset is None or not self._visualizers:
            return

        index = self.visualizer_combo.currentIndex()
        if index < 0 or index >= len(self._visualizers):
            return

        visualizer = self._visualizers[index]
        widget = visualizer.build_widget(self._current_asset)
        self._set_viz_widget(widget)

    def _show_placeholder(self, text: str):
        self._set_viz_widget(QLabel(text))

    def _set_viz_widget(self, widget: QWidget):
        if self._viz_widget is not None:
            self._viz_container.removeWidget(self._viz_widget)
            self._viz_widget.deleteLater()
        self._viz_widget = widget
        self._viz_container.addWidget(widget)

    def _on_export_clicked(self):
        if self._current_asset is None:
            return

        path, _ = QFileDialog.getSaveFileName(self, 'Export Asset', self._current_asset.name, 'All Files (*)')
        if not path:
            return

        with open(path, 'wb') as file:
            file.write(self._current_asset.get_raw_data())
