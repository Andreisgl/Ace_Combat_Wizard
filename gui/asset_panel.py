from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from asset_classes import Asset
from metadata import get_metadata_fields
from visualizers import get_available_visualizers

MODE_AUTO = 'auto'

# (hotkey, digit label, display label, visualizer id to force).
# "3D" has no matching visualizer yet, so forcing it always falls back to
# the auto/default choice below - exactly the desired "not implemented yet"
# behavior, with no special-casing needed.
_MODE_OPTIONS = (
    (Qt.Key_1, '1', 'Auto', MODE_AUTO),
    (Qt.Key_2, '2', 'Raw Data', 'raw_data'),
    (Qt.Key_3, '3', 'Image', 'gim_image'),
    (Qt.Key_4, '4', '3D', 'model_3d'),
)


class AssetPanel(QWidget):
    '''Right-hand panel: export actions, a forced-visualization-mode
    selector, and a pluggable visualization area for whichever asset is
    currently selected in the tree.'''

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_asset: Asset | None = None
        self._visualizers = []
        self._viz_widget: QWidget | None = None
        self._mode = MODE_AUTO

        self.export_button = QPushButton('Export Asset')
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._on_export_clicked)

        button_row = QHBoxLayout()
        button_row.addWidget(self.export_button)

        mode_row = QHBoxLayout()
        self._mode_group = QButtonGroup(self)
        for key, digit, label, mode_id in _MODE_OPTIONS:
            radio = QRadioButton(f'{label} ({digit})')
            radio.setShortcut(QKeySequence(key))
            radio.setChecked(mode_id == MODE_AUTO)
            radio.toggled.connect(lambda checked, m=mode_id: self._on_mode_toggled(checked, m))
            self._mode_group.addButton(radio)
            mode_row.addWidget(radio)

        self.visualizer_combo = QComboBox()
        self.visualizer_combo.currentIndexChanged.connect(self._render_current)

        self._metadata_form = QFormLayout()

        self._viz_container = QVBoxLayout()

        layout = QVBoxLayout(self)
        layout.addLayout(button_row)
        layout.addLayout(mode_row)
        layout.addWidget(self.visualizer_combo)
        layout.addLayout(self._metadata_form)
        # Stretch 1: the viz area claims all leftover vertical space in the
        # panel, instead of shrinking to its content's natural size.
        layout.addLayout(self._viz_container, 1)

        self._show_placeholder('No asset selected')

    def _on_mode_toggled(self, checked: bool, mode_id: str):
        if not checked:
            return
        self._mode = mode_id
        if self._current_asset is not None:
            self._select_visualizer()

    def set_asset(self, asset: Asset | None):
        self._current_asset = asset
        self.export_button.setEnabled(asset is not None)
        self._update_metadata(asset)

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
            self._select_visualizer()

    def _update_metadata(self, asset: Asset | None):
        '''Metadata is per-asset-type, not per-viz-mode, so it's refreshed once
        here rather than alongside visualizer selection/rendering.'''
        while self._metadata_form.rowCount():
            self._metadata_form.removeRow(0)

        if asset is None:
            return

        for label, value in get_metadata_fields(asset):
            value_label = QLabel(value)
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self._metadata_form.addRow(f'{label}:', value_label)

    def _select_visualizer(self):
        '''Picks which visualizer to show for the current asset: the forced
        mode (radio buttons) if it applies to this asset, otherwise the
        type's default (first applicable in registry order, i.e. "auto").'''
        if not self._visualizers:
            return

        index = 0
        if self._mode != MODE_AUTO:
            for i, visualizer in enumerate(self._visualizers):
                if visualizer.id == self._mode:
                    index = i
                    break

        self.visualizer_combo.blockSignals(True)
        self.visualizer_combo.setCurrentIndex(index)
        self.visualizer_combo.blockSignals(False)
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
