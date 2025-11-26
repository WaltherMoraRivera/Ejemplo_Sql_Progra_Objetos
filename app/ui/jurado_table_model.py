from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QColor

from app.domain.models.jurado import Jurado


class JuradoTableModel(QAbstractTableModel):
    """Table model for displaying jurados."""

    SELECT_COLUMN = 0
    ID_COLUMN = 1
    NOMBRE_COLUMN = 2
    CORREO_COLUMN = 3
    ESPECIALIDAD_COLUMN = 4
    PAIS_ORIGIN_COLUMN = 5
    EXPERIENCIA_COLUMN = 6
    TIPO_COLUMN = 7
    ACTION_COLUMN = 8

    def __init__(self):
        super().__init__()
        self.jurados = []
        self.selected_rows = set()

    def rowCount(self, parent=QModelIndex()):
        return len(self.jurados)

    def columnCount(self, parent=QModelIndex()):
        return 9  # checkbox + 7 fields + detail button

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            headers = ["", "ID", "Nombre", "Correo", "Especialidad", "País Origen", "Experiencia (años)", "Tipo", ""]
            return headers[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        jurado = self.jurados[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == self.SELECT_COLUMN:
                return ""
            elif index.column() == self.ID_COLUMN:
                return str(jurado.id)
            elif index.column() == self.NOMBRE_COLUMN:
                return jurado.nombre
            elif index.column() == self.CORREO_COLUMN:
                return jurado.correo
            elif index.column() == self.ESPECIALIDAD_COLUMN:
                return jurado.especialidad
            elif index.column() == self.PAIS_ORIGIN_COLUMN:
                return jurado.pais_origen
            elif index.column() == self.EXPERIENCIA_COLUMN:
                return str(jurado.experiencia_anos)
            elif index.column() == self.TIPO_COLUMN:
                return jurado.tipo_jurado
            elif index.column() == self.ACTION_COLUMN:
                return "Detalle"
        elif role == Qt.ItemDataRole.BackgroundRole and index.row() in self.selected_rows:
            return QColor(200, 220, 255)

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.column() == self.SELECT_COLUMN and role == Qt.ItemDataRole.EditRole:
            if value:
                self.selected_rows.add(index.row())
            else:
                self.selected_rows.discard(index.row())
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        if index.column() == self.SELECT_COLUMN:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def update_jurados(self, jurados: list):
        """Update the jurados list in the table."""
        self.beginResetModel()
        self.jurados = jurados
        self.selected_rows.clear()
        self.endResetModel()

    def get_selected_ids(self) -> list:
        """Return list of selected IDs."""
        return [self.jurados[row].id for row in self.selected_rows]

    def jurado_at(self, row: int) -> Jurado:
        """Get the jurado at a specific row."""
        if 0 <= row < len(self.jurados):
            return self.jurados[row]
        return None

    def clear_selection(self):
        """Clear all selected rows."""
        if self.selected_rows:
            self.selected_rows.clear()
            self.dataChanged.emit(self.index(0, 0), self.index(len(self.jurados) - 1, self.columnCount() - 1))
