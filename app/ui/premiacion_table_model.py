from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QColor

from app.domain.models.premiacion import Premiacion


class PremiacionTableModel(QAbstractTableModel):
    SELECT_COLUMN = 0
    ID_PREMIO_COLUMN = 1
    ID_PELICULA_COLUMN = 2
    CATEGORIA_COLUMN = 3
    EDICION_COLUMN = 4
    POSICION_COLUMN = 5
    DESCRIPCION_COLUMN = 6
    FECHA_COLUMN = 7
    ACTION_COLUMN = 8

    def __init__(self):
        super().__init__()
        self.premiaciones: list[Premiacion] = []
        self.selected_rows = set()

    def rowCount(self, parent=QModelIndex()):
        return len(self.premiaciones)

    def columnCount(self, parent=QModelIndex()):
        return 9

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            headers = ["", "ID Premio", "ID Película", "Categoría", "Edición", "Posición", "Descripción", "Fecha", ""]
            return headers[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        p = self.premiaciones[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == self.SELECT_COLUMN:
                return ""
            elif index.column() == self.ID_PREMIO_COLUMN:
                return str(p.id_premio or "")
            elif index.column() == self.ID_PELICULA_COLUMN:
                return str(p.id_pelicula)
            elif index.column() == self.CATEGORIA_COLUMN:
                return p.categoria
            elif index.column() == self.EDICION_COLUMN:
                return str(p.edicion)
            elif index.column() == self.POSICION_COLUMN:
                return str(p.posicion)
            elif index.column() == self.DESCRIPCION_COLUMN:
                return p.descripcion
            elif index.column() == self.FECHA_COLUMN:
                return str(p.fecha_premiacion or "")
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

    def update_premiaciones(self, premiaciones: list[Premiacion]):
        self.beginResetModel()
        self.premiaciones = premiaciones
        self.selected_rows.clear()
        self.endResetModel()

    def get_selected_ids(self) -> list:
        return [self.premiaciones[row].id_premio for row in self.selected_rows]

    def premiacion_at(self, row: int) -> Premiacion:
        if 0 <= row < len(self.premiaciones):
            return self.premiaciones[row]
        return None

    def clear_selection(self):
        if self.selected_rows:
            self.selected_rows.clear()
            self.dataChanged.emit(self.index(0, 0), self.index(len(self.premiaciones) - 1, self.columnCount() - 1))
