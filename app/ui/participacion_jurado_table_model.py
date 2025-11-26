from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal, QAbstractItemModel
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QPushButton

from app.domain.models.participacion_jurado import ParticipacionJurado


class ParticipacionJuradoTableModel(QAbstractItemModel):
    """Table model for displaying participacion_jurado records."""

    show_detail = pyqtSignal(int, int)  # id_jurado, id_funcion

    def __init__(self, participaciones: list[ParticipacionJurado] | None = None) -> None:
        super().__init__()
        self.participaciones = participaciones or []
        self.selected_rows = set()
        self.ACTION_COLUMN = 5
        self._headers = [
            "",
            "ID Jurado",
            "ID Función",
            "Rol Participación",
            "Comentarios",
            "",
        ]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.participaciones)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole
    ) -> str:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> str:
        if not index.isValid():
            return None

        participacion = self.participaciones[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return ""
            elif index.column() == 1:
                return str(participacion.id_jurado)
            elif index.column() == 2:
                return str(participacion.id_funcion)
            elif index.column() == 3:
                return participacion.rol_participacion
            elif index.column() == 4:
                return participacion.comentarios
            elif index.column() == 5:
                return ""
        elif role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            if index.row() in self.selected_rows:
                return Qt.CheckState.Checked
            return Qt.CheckState.Unchecked
        return None

    def setData(self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            if value == Qt.CheckState.Checked:
                self.selected_rows.add(index.row())
            else:
                self.selected_rows.discard(index.row())
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index: QModelIndex):
        if index.column() == 0:
            return super().flags(index) | Qt.ItemFlag.ItemIsUserCheckable
        return super().flags(index)

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        return self.createIndex(row, column, self.participaciones[row])

    def parent(self, index: QModelIndex) -> QModelIndex:
        return QModelIndex()

    def hasChildren(self, parent: QModelIndex = QModelIndex()) -> bool:
        if parent.isValid():
            return False
        return len(self.participaciones) > 0

    def update_participaciones(self, participaciones: list[ParticipacionJurado]) -> None:
        """Update the model with new participaciones."""
        self.beginResetModel()
        self.participaciones = participaciones
        self.selected_rows.clear()
        self.endResetModel()

    def get_selected_ids(self) -> list[tuple]:
        """Get the composite IDs of checked participaciones."""
        result = []
        for row in self.selected_rows:
            if 0 <= row < len(self.participaciones):
                p = self.participaciones[row]
                result.append((p.id_jurado, p.id_funcion))
        return result

    def participacion_at(self, row: int) -> ParticipacionJurado:
        """Get the participacion at a specific row."""
        if 0 <= row < len(self.participaciones):
            return self.participaciones[row]
        return None

    def clear_selection(self):
        """Clear all selected rows."""
        if self.selected_rows:
            self.selected_rows.clear()
            self.dataChanged.emit(self.index(0, 0), self.index(len(self.participaciones) - 1, self.columnCount() - 1))

    def create_detail_button(self, row: int) -> QPushButton:
        """Create a detail button for a specific row."""
        btn = QPushButton("👁")
        btn.setMaximumWidth(40)
        btn.clicked.connect(lambda: self._on_detail_clicked(row))
        return btn

    def _on_detail_clicked(self, row: int) -> None:
        """Handle detail button click."""
        if 0 <= row < len(self.participaciones):
            p = self.participaciones[row]
            self.show_detail.emit(p.id_jurado, p.id_funcion)
